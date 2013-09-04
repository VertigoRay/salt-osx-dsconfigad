'''
A module to wrap dsconfigad calls

:maintainer:    Raymond Piller <ray@vertigion.com>
:maturity:      new
:depends:       
:platform:      Darwin
'''

# Import python libs
import base64
import difflib
import logging
import plistlib
import re
import socket
import xml

# Import salt libs
import salt.utils

log = logging.getLogger(__name__)
ret = {
    'state': 'dsconfigad',
    'fun': '',
    'name': 'dsconfigad', # the name argument passed to all states
    'changes': {},
    'result': False,
    'comment': '',
}


# dsconfigad -show returns human readable fields, this maps them to settings.
dsconfig_map = {
    'active directory domain':          'domain',
    'active directory forest':          'forest',
    'allowed admin groups':             'groups',
    'authentication from any domain':   'alldomains',
    'computer account':                 'computer',
    'create mobile account at login':   'mobile',
    'force home to startup disk':       'localhome',
    'generate kerberos authority':      'authority',
    'group gid mapping':                'ggid',
    'mapping group gid to attribute':   'ggid',
    'mapping uid to attribute':         'uid',
    'mapping user gid to attribute':    'gid',
    'mount home as sharepoint':         'sharepoint',
    'namespace mode':                   'namespace',
    'network protocol':                 'protocol',
    'packet encryption':                'packetencrypt',
    'packet signing':                   'packetsign',
    'password change interval':         'passinterval',
    'preferred domain controller':      'preferred',
    'require confirmation':             'mobileconfirm',
    'restrict dynamic dns updates':     'restrictddns',
    'uid mapping':                      'uid',
    'use windows unc path for home':    'useuncpath',
    'user gid mapping':                 'gid',
    'shell':                            'shell',
}

# this associates a setting with allowed inputs for that setting
dsconfig_adv = {
    'mobile':       ('disable', 'enable'),
    'mobileconfirm':('disable', 'enable'),
    'localhome':    ('disable', 'enable'),
    'sharepoint':   ('disable', 'enable'),
    'useuncpath':   ('disable', 'enable'),
    'protocol':     ('', 'afp', 'smb', 'nfs'),
    'shell':        '',
    'uid':          (False, ()),
    'gid':          (False, ()),
    'ggid':         (False, ()),
    'authority':    ('disable', 'enable'),
    'preferred':    (False, ''),
    'groups':       (False, ()),
    'alldomains':   ('disable', 'enable'),
    'packetsign':   ('disable', 'allow', 'require'),
    'packetencrypt':('disable', 'allow', 'require', 'ssl'),
    'passinterval': '',
    'restrictddns': (),
    'namespace':    ('', 'forest', 'domain'),
}


def __virtual__():
    '''
    Set the virtual pkg module if the kernel is Darwin
    '''
    return 'dsconfigad' if salt.utils.is_darwin() else False


def _ret_comment(comment, res):
    comment = comment + '%(pid)s%(retcode)s%(stdout)s%(stderr)s\n' if __salt__['config.get']('is_test_computer', False) else '%s\n' % comment
    return comment % {
        'pid':" <pid '%s'>" % res['pid'], 
        'retcode':"<retcode '%s'>" % res['retcode'], 
        'stdout':"<stdout '%s'>" % res['stdout'] if res['retcode'] != 0 else '', 
        'stderr':"<stderr '%s'>" % res['stderr'] if res['retcode'] != 0 else '',
    }


def _is_set(**kwargs):
    '''
    Validate the supplied option -- comparing the desired option with the current setting.

    gloabl dsconfig_adv is used here to help determine the expected values.  Not
    necessarily LBYL, but needed for proper data comparison.
    
    option          the desired option as suppled via a function call or in pillar[dsconfigad].
                    True only if all supplied options (kwargs) are True.

                    Usage:  option = value
                    Example:  domain = 'example.com'

    Returns bool
    
    The current setting will be pulled from show('xml')
    '''
    
    log.info('> _is_set()')
    log.debug('> _is_set(%s %s)' % (kwargs, type(kwargs)))
    ret['fun'] = 'is_set'

    settings = {}
    try:
        # build settings dict so we can compare to desired options.
        # this wasn't done globally so that settings would always be accurate, even after changes in the middle of an iteration.
        for k1, v1 in plistlib.readPlistFromString(show('xml')).iteritems():
            try:
                try:
                    settings[dsconfig_map[k1.lower()]] = v1.lower()
                
                except AttributeError as e:
                    log.debug('! is_set: AttributeError: %s' % e)
                    settings[dsconfig_map[k1.lower()]] = v1

            except KeyError as e:
                log.debug('! is_set: KeyError: %s' % e)
                # Headings aren't keyed in dsconfig_map.
                # Assume is header and check v if dict and traverse
                try:
                    for k2, v2 in v1.iteritems():
                        try:
                            settings[dsconfig_map[k2.lower()]] = v2.lower()
                        
                        except KeyError as e:
                            # dsconfig_map key doesn't exist, so pass
                            log.debug('! is_set: KeyError: %s' % e)
                        
                        except AttributeError as e:
                            # .lower() is not valid attribute on v2
                            log.debug('! is_set: AttributeError: %s' % e)
                            settings[dsconfig_map[k2.lower()]] = v2
                
                except TypeError as e:
                    log.debug('~ is_set: TypeError: %s' % e)

        log.debug('~ is_set: settings (dirty): %s' % settings)
        
        # if restrictddns didn't get parsed into settings, it's set to False
        # we set it here to prevent issues with settings not matching
        if 'restrictddns' not in settings:
            log.debug('! is_set: restrictddns not in settings: False')
            settings['restrictddns'] = False

        # groups needs to be a list, if it's a str
        try:
            settings['groups'] = [settings['groups']] if type(settings['groups']) is str else settings['groups']
        
        except KeyError as e:
            # if groups not in settings, then it is set to False
            settings['groups'] = False


    except xml.parsers.expat.ExpatError as e:
        # dsconfigad -show -xml is empty: computer not bound
        # pass; cause setting check below will catch mismatches and respond properly.
        log.debug('! is_set: ExpatError: %s' % e)


    log.debug('~ is_set: settings (clean): %s' % settings)

    for k, v in kwargs.iteritems():
        k = k.lower()
        try:
            v = v.lower()
        except AttributeError as e:
            # .lower() is not valid attribute on v
            log.debug('! is_set: AttributeError: %s' % e)

        if k == 'computer':
            # domain object ends in $
            # add $ to end of local computer name before comparison.
            v += '$'
        
        if k.lower() == 'restrictddns':
            # restrictddns is an oddball.
            # It'll show up as str('') when it needs to be disabled, but bool(False) makes more sense
            if len(v.strip()) == 0:
                v = False

        if k in settings:
            log.debug('~ is_set: kwarg[%s] == %s %s; settings[%s] == %s %s' % (k, v, type(v), k, settings[k], type(settings[k])))

            try:
                if v == settings[k]:
                    log.debug('~ is_set: %s == %s' % (v, settings[k]))
                    continue
                
                elif sorted(v) == sorted(settings[k]):
                    log.debug('~ is_set: sorted(%s) == sorted(%s)' % (settings[k], type(settings[k]), v, type(v), sorted(settings[k]), sorted(v)))
                    continue

                elif type(v) != type(settings[k]):
                    log.debug('~ is_set: type(kwarg) != type(setting)')
                    
                    # if types don't match, we'll assume that one is list and the other is something else
                    # make sure both are list and then compare sorted()
                    if type(v) is not list:
                        log.debug('~ is_set: type(v) is not list; converting to list')
                        v_temp = [v]
                    
                    if type(settings[k]) is not list:
                        log.debug('~ is_set: type(settings[k]) is not list; converting to list')
                        setting_temp = [settings[k]]

                    if sorted(v) == sorted(settings[k]):
                        log.debug('~ is_set: sorted(%s) == sorted(%s)' % (settings[k], type(settings[k]), v, type(v), sorted(settings[k]), sorted(v)))
                        continue

                else:
                    log.debug('< is_set: False (kwarg != setting)')
                    return False
                    
            except TypeError as e:
                # likely not a sortable v, and since made it past main if, likely is not equal
                log.debug('! is_set: TypeError: %s' % e)
                return False

        else:
            log.debug('~ is_set: %s not in settings' % k)

            try:
                if dsconfig_adv[k][0] == False:
                    # Settings with a -no variant (-noguid, -nogroups, etc.) will not show up in current settings XML.
                    # Since is not in current settings at this point, we just need to check if the desired option (v) is bool(False).
                    log.debug('~ is_set: has a -no variant ...')
                    if v == False:
                        continue
                    else:
                        log.debug('< is_set: False (%s is not False)' % k)
                        return False

            except IndexError as e:
                log.debug('< is_set: False (%s not in settings)' % k)
                return False

            except KeyError as e:
                log.debug('< is_set: False (%s not in settings)' % k)
                return False

    log.debug('< is_set: True')
    return True


def add(**kwargs):
    '''
    Add the computer to the domain

    kwargs:
    domain *        fully qualified DNS name of Active Directory Domain
    ou *            (CN=Computers) fully qualified LDAP DN of container for the computer
    force           (True) force the process (i.e., join the existing account)
    forest *        fully qualified DNS name of Active Directory Forest
    username *      username of a priveleged network user
    password *      password of a priveleged network user
    localuser *     username of a priveleged local user
    localpassword * username of a priveleged local user
    computer *      (hostname) name of computer to add to domain

    * will look in pillar[dsconfigad] if not provided
    '''

    log.info('> add()')
    log.debug('> add(%s %s)' % (kwargs, type(kwargs)))
    ret['fun'] = 'add'
    before = show()

    username = base64.b64decode(kwargs.pop('init_u')) if 'init_u' in kwargs else kwargs.pop('username', None)
    password = base64.b64decode(kwargs.pop('init_p')) if 'init_p' in kwargs else kwargs.pop('password', None)
    localuser = base64.b64decode(kwargs.pop('init_lu')) if 'init_lu' in kwargs else kwargs.pop('localuser', None)
    localpassword = base64.b64decode(kwargs.pop('init_lp')) if 'init_lp' in kwargs else kwargs.pop('localpassword', None)
    forest = kwargs.pop('forest', None)
    domain = kwargs.pop('domain', None)
    ou = kwargs.pop('ou', None)
    computer = kwargs.pop('computer', None)
    preferred = kwargs.pop('preferred', None)
    force = kwargs.pop('force', None)

    # Get encoded configuration from pillar
    if not username:
        username = base64.b64decode(__salt__['config.get']('dsconfigad:init_u', ''))
    if not password:
        password = base64.b64decode(__salt__['config.get']('dsconfigad:init_p', ''))
    if not localuser:
        localuser = base64.b64decode(__salt__['config.get']('dsconfigad:init_lu', ''))
    if not localpassword:
        localpassword = base64.b64decode(__salt__['config.get']('dsconfigad:init_lp', ''))

    # If not encoded, try plain text. Get encoded configuration from pillar
    if not username:
        username = __salt__['config.get']('dsconfigad:username', None)
    if not password:
        password = __salt__['config.get']('dsconfigad:password', None)
    if not localuser:
        localuser = __salt__['config.get']('dsconfigad:localuser', None)
    if not localpassword:
        localpassword = __salt__['config.get']('dsconfigad:localpassword', None)
    if not forest:
        forest = __salt__['config.get']('dsconfigad:forest', None)
    if not domain:
        domain = __salt__['config.get']('dsconfigad:domain', None)
    if not ou:
        ou = __salt__['config.get']('dsconfigad:ou', None)
    if not computer:
        computer = __salt__['config.get']('dsconfigad:computer', socket.gethostname())
    if not preferred:
        preferred = __salt__['config.get']('dsconfigad:preferred', None)

    if not username:
        return False

    if forest:
        is_set_res = _is_set(forest=forest, domain=domain, computer=computer)
    else:
        is_set_res = _is_set(domain=domain, computer=computer)

    log.debug('~ add: is_set_res: %s' % is_set_res)
    if is_set_res:
        ret['result'] = True
        ret['comment'] = ('Computer %s is already bound to domain %s' % (computer, domain))
        return ret
    else:
        dsconfigad = salt.utils.which('dsconfigad')

        cmd = '%(dsconfigad)s -add%(computer)s%(ou)s%(preferred)s%(username)s%(password)s%(localuser)s%(localpassword)s%(force)s' % {
            'dsconfigad':dsconfigad,
            'force':' -force' if salt.utils.is_true(kwargs.get('force', True)) else '',
            'computer':' -computer "%s"' % computer if computer else '',
            'ou':' -ou "%s"' % ou if ou else '',
            'preferred':' -preferred "%s"' % preferred if preferred else '',
            'username':' -username "%s"' % username if username else '',
            'password':' -password "%s"' % password if password else '',
            'localuser':' -localuser "%s"' % localuser if localuser else '',
            'localpassword':' -localpassword "%s"' % localpassword if localpassword else '',
        }

        log.debug('~ add: cmd.run_all (quiet): %s' % cmd)
        # run quietly to prevent passwords from showing in info log.
        res = __salt__['cmd.run_all'](cmd, quiet=True)
        log.debug('~ add: cmd.run_all res: %s' % res)

        ret['changes']['diff'] = ''.join(difflib.unified_diff(before.splitlines(True), show().splitlines(True), fromfile='dsconfigad -show', tofile='dsconfigad -show'))

        if res['retcode'] != 0:
            ret['comment'] += _ret_comment('Failed to add this computer (%s) to the domain: %s' % (computer, domain), res)
            ret['result'] = False
            return ret

        ret['comment'] += _ret_comment('Successfully added this computer (%s) to the domain: %s' % (computer, domain), res)
        ret['result'] = True
        return ret


def bind(**kwargs):
    '''
    Bind the computer

    this is just calls add followed by config
    '''

    log.info('> bind()')
    log.debug('> bind(%s %s)' % (kwargs, type(kwargs)))
    
    global ret

    # Check to see if we're calling from a state ...
    # http://docs.saltstack.com/ref/states/all/salt.states.module.html#module-salt.states.module
    if '__pub_fun' not in kwargs:
        ret['m_fun'] = 'bind'
        ret['m_name'] = 'dsconfigad'

    before = show()

    ret_add = add(**kwargs)
    log.debug('~ bind: ret_add: %s' % ret_add)

    if ret_add['result'] == False:
        log.debug('! bind: ret_add: result == false; Done!')
        ret['fun'] = 'bind'
        return ret_add

    log.debug('~ bind: overwrite global ret so config() just adds to it.')
    
    ret = ret_add

    # need a newlinee on comment for aesthetics.
    ret['comment'] += '\n'

    ret_cnf = config(**kwargs)
    log.debug('~ bind: ret_cnf: %s' % ret_cnf)

    ret_cnf['changes']['diff'] = ''.join(difflib.unified_diff(before.splitlines(True), show().splitlines(True), fromfile='dsconfigad -show', tofile='dsconfigad -show'))
    log.debug('~ bind: changes diff: %s' % ret_cnf['changes']['diff'])
    
    ret['fun'] = 'bind'
    
    log.debug('< bind: %s' % ret_cnf)
    return ret_cnf


def config(use_pillar=False, **kwargs):
    '''
    Configure advanced options

    use_pillar      (False) apply all advanced options from pillar[dsconfigad]
                    if set, all kwargs are ignored
                    if len(kwargs) == 0: use_pillar = True

    kwargs:
    localuser *     username of a priveleged local user
    localpassword * username of a priveleged local user
    mobile          mobile user accounts for offline use
    mobileconfig    warning for mobile account creation 
    localhome       force home directory to local drive
    useuncpath      use Windows UNC for network home
    protocol        changes protocol used when mounting home
    shell           (/bin/bash) specify a default shell
    uid             name of attribute to be used for UNIX uid field
    gid             name of attribute to be used for UNIX gid field
    ggid            name of attribute to be used for UNIX group gid field
    authority       generation of Kerberos authority
    preferred       fully-qualified domain name of preferred server to query
    groups          list of groups that are granted Admin privelages on local workstation
    alldomains      allow authentication from any domain
    packetsign      config packet signing
    packetencrypt   config packet encryption
    namespace       where forest qualifies all usernames
    passinterval    how oftern to change computer trust account password, in days
    restrictddns    list of interfaces to restrict DDNS to (en0, en1, etc.)

    * will look in pillar[dsconfigad] if not provided 
    '''

    log.info('> config()')
    log.debug('> config(%s %s, %s %s)' % (use_pillar, type(use_pillar), kwargs, type(kwargs)))
    ret['fun'] = 'config'
    before = show()
    
    localuser = base64.b64decode(kwargs.pop('init_lu')) if 'init_lu' in kwargs else kwargs.pop('localuser', None)
    localpassword = base64.b64decode(kwargs.pop('init_lp')) if 'init_lp' in kwargs else kwargs.pop('localpassword', None)

    # Get encoded configuration from pillar
    if not localuser:
        localuser = base64.b64decode(__salt__['config.get']('dsconfigad:init_lu', ''))
    if not localpassword:
        localpassword = base64.b64decode(__salt__['config.get']('dsconfigad:init_lp', ''))

    # If not encoded, try plain text. Get encoded configuration from pillar
    if not localuser:
        localuser = __salt__['config.get']('dsconfigad:localuser', None)
    if not localpassword:
        localpassword = __salt__['config.get']('dsconfigad:localpassword', None)

    # kwargs contains __kwargs (private kwargs) that need to be excluded -- added by salt
    # process loops through kwargs and deletes from cust_kwargs to avoid RuntimeError.
    cust_kwargs = dict(kwargs)
    for k, v in kwargs.iteritems():
        if k.startswith('__'):
            log.debug('~ config: removing private kwarg: %s' % k)
            del cust_kwargs[k]

    use_pillar = True if len(cust_kwargs) == 0 else use_pillar

    if use_pillar:
        adv_opts = __salt__['config.get']('dsconfigad')
    else:
        adv_opts = cust_kwargs

    log.debug('~ config: adv_opts: %s' % adv_opts)

    for k, v in adv_opts.iteritems():
        log.debug('~ config: adv_opt: %s: %s' % (k, v))
        if k not in dsconfig_adv:
            log.debug('~ config: %s not in dsconfig_adv')
            continue

        elif _is_set(**{k:v}):
            log.info('~ config: The option %s is already set to %s' % (k, v))
            ret['result'] = True
            if __salt__['config.get']('is_test_computer', False):
                ret['comment'] += '%s == %s %s\n' % (k, v, type(v))

            continue

        else:
            log.debug('~ config: Setting %s to %s' % (k, v))
            dsconfigad = salt.utils.which('dsconfigad')

            # options that expect enable/disable are stored as True/False.  This fixes that.
            if len(dsconfig_adv[k]) == 2 and 'enable' in dsconfig_adv[k] and 'disable' in dsconfig_adv[k]:
                v = dsconfig_adv[k][v]

            # this needs to stay right before cmd to prevent other KeyErrors
            if k == 'restrictddns':
                # restringDDNS is case sensitive
                k = 'restrictDDNS'

                # restrictDDNS requires str('') instead of bool(False)
                if type(v) is bool and v == False:
                    v = ''

            if type(v) is list:
                v = ','.join(v)

            try:
                if dsconfig_adv[k][0] == False:
                    # Settings with a -no variant (-noguid, -nogroups, etc.) need to have k changed.
                    log.debug('~ config: has a -no variant ...')
                    if v == False:
                        k = 'no%s' % k

            except IndexError as e:
                pass

            cmd = '%(dsconfigad)s -%(option)s "%(value)s"%(localuser)s%(localpassword)s' % {
                'dsconfigad':dsconfigad,
                'option':k,
                'value':v,
                'localuser':' -localuser "%s"' % localuser if localuser else '',
                'localpassword':' -localpassword "%s"' % localpassword if localpassword else '',
            }

            log.debug('~ config: cmd.run_all (quiet): %s' % cmd)
            # run quietly to prevent passwords from showing in info log.
            res = __salt__['cmd.run_all'](cmd, quiet=True)
            log.debug('~ config: cmd.run_all res: %s' % res)

            log.info('~ config: The option %s is now set to %s' % (k, v))
            if __salt__['config.get']('is_test_computer', False):
                ret['comment'] += _ret_comment('%(k)s = %(v)s %(type)s' % {
                    'k':k,
                    'v':v,
                    'type':type(v),
                }, res)
            
            if res['retcode'] != 0:
                ret['result'] = False
                ret['changes']['diff'] = ''.join(difflib.unified_diff(before.splitlines(True), show().splitlines(True), fromfile='dsconfigad -show', tofile='dsconfigad -show'))
                return ret

    ret['result'] = True
    ret['changes']['diff'] = ''.join(difflib.unified_diff(before.splitlines(True), show().splitlines(True), fromfile='dsconfigad -show', tofile='dsconfigad -show'))
    if len(ret['changes']['diff'].strip()) == 0:
        ret['comment'] += 'No configuration changes necessary.'
    
    else:
        ret['comment'] += 'Configuration changes made successfully.'

    return ret


def remove(**kwargs):
    '''
    Remove the computer from domain

    kwargs:
    force *         (True) force the process (i.e., join the existing account)
    username *      username of a priveleged network user
    password *      password of a priveleged network user
    localuser *     username of a priveleged local user
    localpassword * username of a priveleged local user

    * will look in pillar[dsconfigad] if not provided
    '''
    
    log.info('> remove()')
    log.debug('> remove(%s %s)' % (kwargs, type(kwargs)))
    ret['fun'] = 'remove'
    before = show()

    if before.strip() == '':
        ret['result'] = True
        ret['comment'] = ('Computer is already NOT bound to a domain')
        return ret

    username = base64.b64decode(kwargs.pop('init_u')) if 'init_u' in kwargs else kwargs.pop('username', None)
    password = base64.b64decode(kwargs.pop('init_p')) if 'init_p' in kwargs else kwargs.pop('password', None)
    localuser = base64.b64decode(kwargs.pop('init_lu')) if 'init_lu' in kwargs else kwargs.pop('localuser', None)
    localpassword = base64.b64decode(kwargs.pop('init_lp')) if 'init_lp' in kwargs else kwargs.pop('localpassword', None)
    force = kwargs.pop('force', True)
    
    # Get encoded configuration from pillar
    if not username:
        username = base64.b64decode(__salt__['config.get']('dsconfigad:init_u', ''))
    if not password:
        password = base64.b64decode(__salt__['config.get']('dsconfigad:init_p', ''))
    if not localuser:
        localuser = base64.b64decode(__salt__['config.get']('dsconfigad:init_lu', ''))
    if not localpassword:
        localpassword = base64.b64decode(__salt__['config.get']('dsconfigad:init_lp', ''))

    # If not encoded, try plain text. Get encoded configuration from pillar
    if not username:
        username = __salt__['config.get']('dsconfigad:username', None)
    if not password:
        password = __salt__['config.get']('dsconfigad:password', None)
    if not localuser:
        localuser = __salt__['config.get']('dsconfigad:localuser', None)
    if not localpassword:
        localpassword = __salt__['config.get']('dsconfigad:localpassword', None)

    if not username:
        return False

    dsconfigad = salt.utils.which('dsconfigad')

    cmd = '%(dsconfigad)s -remove%(username)s%(password)s%(localuser)s%(localpassword)s%(force)s' % {
        'dsconfigad':dsconfigad,
        'force':' -force' if force else '',
        'username':' -username "%s"' % username if username else '',
        'password':' -password "%s"' % password if password else '',
        'localuser':' -localuser "%s"' % localuser if localuser else '',
        'localpassword':' -localpassword "%s"' % localpassword if localpassword else '',
    }

    log.debug('~ remove: cmd.run_all (quiet): %s' % cmd)
    # run quietly to prevent passwords from showing in info log.
    res = __salt__['cmd.run_all'](cmd, quiet=True)
    log.debug('~ remove: cmd.run_all res: %s' % res)

    ret['changes']['diff'] = ''.join(difflib.unified_diff(before.splitlines(True), show().splitlines(True), fromfile='dsconfigad -show', tofile='dsconfigad -show'))
    
    if res['retcode'] != 0:
        ret['comment'] += _ret_comment('Failed to remove this computer from domain.', res)
        ret['result'] = False
        return ret

    ret['comment'] += _ret_comment('Successfully removed this computer from domain.', res)
    ret['result'] = True
    return ret


def show(format=False):
    '''
    Show current configuration for Active Directory

    CLI Example:

    .. code-block:: bash

        salt '*' dsconfigad.show
        salt '*' dsconfigad.show xml
    '''

    log.info('> show(format=%s)' % format)
    ret['fun'] = 'show'
    
    if type(format) is bool and not format:
        return __salt__['cmd.run'](
            'dsconfigad -show'
        )
    elif format == 'xml':
        return __salt__['cmd.run'](
            'dsconfigad -show -xml'
        ).strip()
    else:
        return False


def test(**kwargs):
    '''
    Testing returning states

    CLI Example:

    .. code-block:: bash

        salt '*' dsconfigad.test
    '''
    log.info('> test(%s)' % kwargs)
    
    ret['fun'] = 'test'
    ret['comment'] = 'kwargs: %s' % kwargs

    return [ret]
