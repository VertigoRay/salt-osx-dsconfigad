'''
A module to wrap dsconfigad calls

:maintainer:  VertigoRay
:maturity:		new
:depends:		
:platform:		Darwin
'''

# Import python libs
import base64
import difflib
import logging
import plistlib
import re
import socket

# Import salt libs
import salt.utils

log = logging.getLogger(__name__)
ret = {'name': 'dsconfigad', 'changes': {}, 'result': False, 'comment': ''}

# dsconfigad -show returns human readable fields, this maps them to settings.
dsconfig_map = {
	'authentication from any domain':	'alldomains',
	'generate kerberos authority':		'authority',
	'computer account':					'computer',
	'active directory domain':			'domain',
	'active directory forest':			'forest',
	'mapping group gid to attribute':	'ggid',
	'mapping user gid to attribute':	'gid',
	'allowed admin groups':				'groups',
	'force home to startup disk':		'localhome',
	'create mobile account at login':	'mobile',
	'require confirmation':				'mobileconfirm',
	'namespace mode':					'namespace',
	'packet encryption':				'packetencrypt',
	'packet signing':					'packetsign',
	'password change interval':			'passinterval',
	'preferred domain controller':		'preferred',
	'network protocol':					'protocol',
	'restrict dynamic dns updates':		'restrictddns',
	'mount home as sharepoint':			'sharepoint',
	'shell':							'shell',
	'mapping uid to attribute':			'uid',
	'use windows unc path for home':	'useuncpath',
}

# this associates a setting with allowed inputs for that setting
dsconfig_adv = {
	'mobile':		('disable', 'enable'),
	'mobileconfirm':('disable', 'enable'),
	'localhome':	('disable', 'enable'),
	'sharepoint':	('disable', 'enable'),
	'useuncpath':	('disable', 'enable'),
	'protocol':		('', 'afp', 'smb', 'nfs'),
	'shell':		'',
	'uid':			(False, ()),
	'gid':			(False, ()),
	'ggid':			(False, ()),
	'authority':	('disable', 'enable'),
	'preferred':	(False, ''),
	'groups':		(False, ()),
	'alldomains':	('disable', 'enable'),
	'packetsign':	('disable', 'allow', 'require'),
	'packetencrypt':('disable', 'allow', 'require', 'ssl'),
	'passinterval':	'',
	'restrictddns':	(),
	'namespace':	('', 'forest', 'domain'),
}


def __virtual__():
	'''
	Set the virtual pkg module if the kernel is Darwin
	'''
	return 'dsconfigad' if salt.utils.is_darwin() else False


def is_set(**kwargs):
	'''
	Validate the supplied option -- comparing the desired option with the current setting.

	gloabl dsconfig_adv is used here to help determine the expected values.  Not
	necessarily LBYL, but needed for proper data comparison.
	
	option 			the desired option as suppled via a function call or in pillar[dsconfigad].
					True only if all supplied options (kwargs) are True.

					Usage:  option = value
					Example:  domain = 'example.com'

	Returns bool
	
	The current setting will be pulled from show('xml')
	'''
	
	log.debug('> is_set(%s)' % kwargs)

	settings = {}
	for k, v in (plistlib.readPlistFromString(show('xml').strip())).iteritems():
		settings[dsconfig_map[k.lower()]] = v

	log.debug('~ is_set: settings: %s' % settings)

	for k, v in kwargs:
		k = k.lower()
		log.debug('~ is_set: kwarg[%s] == %s; settings[%s] == %s' % (k, v, k, settings[k]))

		if k in settings:
			if settings[k] == v:
				log.debug('~ is_set: settings[k] == v')
				continue
			elif type(settings[k]) is not str and type(v) is not str and sorted(settings[k]) == sorted(v):
				log.debug('~ is_set: type(%s) is %s; type(%s) is %s; sorted(%s) == sorted(%s)' % (settings[k], type(settings[k]), v, type(v), sorted(settings[k]), sorted(v)))
				continue
			else:
				log.debug('< is_set: False (kwarg != setting)')
				return False
		else:
			log.debug('< is_set: False (%s not in settings)' % k)
			return False

	log.debug('< is_set: True')
	return True


def add(**kwargs):
	'''
	Add the computer to the domain

	kwargs:
	domain *		fully qualified DNS name of Active Directory Domain
	ou *			(CN=Computers) fully qualified LDAP DN of container for the computer
	force			(True) force the process (i.e., join the existing account)
	forest *		fully qualified DNS name of Active Directory Forest
	username *		username of a priveleged network user
	password *		password of a priveleged network user
	localuser *		username of a priveleged local user
	localpassword *	username of a priveleged local user
	computer *		(hostname) name of computer to add to domain

	* will look in pillar[dsconfigad] if not provided
	'''

	before = show()

	username = base64.b64decode(kwargs.pop('init_u')) if 'init_u' in kwargs else kwargs.pop('username', None)
	password = base64.b64decode(kwargs.pop('init_p')) if 'init_p' in kwargs else kwargs.pop('password', None)
	localuser = base64.b64decode(kwargs.pop('init_lu')) if 'init_lu' in kwargs else kwargs.pop('localuser', None)
	localpassword = base64.b64decode(kwargs.pop('init_lp')) if 'init_lp' in kwargs else kwargs.pop('localpassword', None)
	forest = kwargs.pop('forest', None)
	domain = kwargs.pop('domain', None)
	ou = kwargs.pop('ou', None)
	computer = kwargs.pop('computer', None)
	force = kwargs.pop('force', None)

	# Get encoded configuration from pillar
	if not username:
		username = base64.b64decode(__salt__['config.get']('dsconfigad:init_u', None))
	if not password:
		password = base64.b64decode(__salt__['config.get']('dsconfigad:init_p', None))
	if not localuser:
		localuser = base64.b64decode(__salt__['config.get']('dsconfigad:init_lu', None))
	if not localpassword:
		localpassword = base64.b64decode(__salt__['config.get']('dsconfigad:init_lp', None))

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

	if not username:
		return False

	if forest:
		is_set = is_set(forest=forest, domain=domain, computer=computer)
	else:
		is_set = is_set(domain=domain, computer=computer)

	if is_set:
		ret['result'] = True
		ret['comment'] = ('Computer %s is already bound to domain %s' % (computer, domain))
		return ret
	else:
		res = __salt__['cmd.run'](
			'dsconfigad -add%(force)s%(computer)s%(ou)s%(preferred)s%(username)s%(password)s%(localuser)s%(localpassword)s' % {
				'force':' -force' if salt.utils.is_true(kwargs.get('force', True)) else None,
				'computer':' -computer "%s"' % computer if computer else None,
				'ou':' -ou "%s"' % ou if ou else None,
				'preferred':' -preferred "%s"' % preferred if preferred else None,
				'username':' -username "%s"' % username if username else None,
				'password':' -password "%s"' % password if password else None,
				'localuser':' -localuser "%s"' % localuser if localuser else None,
				'localpassword':' -localpassword "%s"' % localpassword if localpassword else None,
			}
		)

		ret['changes']['diff'] = ''.join(difflib.unified_diff(before, show()))
		ret['comment'] = ('dsconfigad: %s\nPID: %s; RetCode: %s\n%s' % (res['stdout'], res['pid'], res['retcode'], res['stderr']))

		if res['retcode'] != 0:
			ret['result'] = False
			return ret

		ret['result'] = True
		return ret


def config(use_pillar=False, **kwargs):
	'''
	Configure advanced options

	use_pillar		(False) apply all advanced options from pillar[dsconfigad]
					if set, all kwargs are ignored

	kwargs:
	localuser *		username of a priveleged local user
	localpassword *	username of a priveleged local user
	mobile 			mobile user accounts for offline use
	mobileconfig	warning for mobile account creation 
	localhome		force home directory to local drive
	useuncpath		use Windows UNC for network home
	protocol		changes protocol used when mounting home
	shell			(/bin/bash) specify a default shell
	uid				name of attribute to be used for UNIX uid field
	gid 			name of attribute to be used for UNIX gid field
	ggid			name of attribute to be used for UNIX group gid field
	authority		generation of Kerberos authority
	preferred		fully-qualified domain name of preferred server to query
	groups			list of groups that are granted Admin privelages on local workstation
	alldomains		allow authentication from any domain
	packetsign		config packet signing
	packetencrypt	config packet encryption
	namespace		where forest qualifies all usernames
	passinterval	how oftern to change computer trust account password, in days
	restrictddns	list of interfaces to restrict DDNS to (en0, en1, etc.)

	* will look in pillar[dsconfigad] if not provided 
	'''

	before = show()
	
	localuser = base64.b64decode(kwargs.pop('init_lu')) if 'init_lu' in kwargs else kwargs.pop('localuser', None)
	localpassword = base64.b64decode(kwargs.pop('init_lp')) if 'init_lp' in kwargs else kwargs.pop('localpassword', None)

	# Get encoded configuration from pillar
	if not localuser:
		localuser = base64.b64decode(__salt__['config.get']('dsconfigad:init_lu', None))
	if not localpassword:
		localpassword = base64.b64decode(__salt__['config.get']('dsconfigad:init_lp', None))

	# If not encoded, try plain text. Get encoded configuration from pillar
	if not localuser:
		localuser = __salt__['config.get']('dsconfigad:localuser', None)
	if not localpassword:
		localpassword = __salt__['config.get']('dsconfigad:localpassword', None)

	if use_pillar:
		adv_opts = __salt__['config.get']('dsconfigad')
	else:
		adv_opts = kwargs

	for k, v in adv_opts.iteritems():
		if is_set(**{k:v}):
			ret['result'] = True
			ret['comment'] += ('The option %s is already set to %s.\n' % (k,v))
			continue
		else:
			res = __salt__['cmd.run'](
				'dsconfigad -%(option)s "%(value)s" %(localuser)s%(localpassword)s' % {
					'option':k,
					'value':v,
					'localuser':' -localuser "%s"' % localuser if localuser else None,
					'localpassword':' -localpassword "%s"' % localpassword if localpassword else None,
				}
			)

			ret['comment'] += ('dsconfigad: %s\nPID: %s; RetCode: %s\n%s\n' % (res['stdout'], res['pid'], res['retcode'], res['stderr']))
			if res['retcode'] != 0:
				ret['result'] = False
				ret['changes']['diff'] = ''.join(difflib.unified_diff(before, show()))
				break

	ret['result'] = True
	ret['changes']['diff'] = ''.join(difflib.unified_diff(before, show()))
	return ret


def remove(**kwargs):
	'''
	Remove the computer from domain

	kwargs:
	force *			(True) force the process (i.e., join the existing account)
	username *		username of a priveleged network user
	password *		password of a priveleged network user
	localuser *		username of a priveleged local user
	localpassword *	username of a priveleged local user

	* will look in pillar[dsconfigad] if not provided
	'''
	
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
		username = base64.b64decode(__salt__['config.get']('dsconfigad:init_u', None))
	if not password:
		password = base64.b64decode(__salt__['config.get']('dsconfigad:init_p', None))
	if not localuser:
		localuser = base64.b64decode(__salt__['config.get']('dsconfigad:init_lu', None))
	if not localpassword:
		localpassword = base64.b64decode(__salt__['config.get']('dsconfigad:init_lp', None))

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

	res = __salt__['cmd.run'](
		'dsconfigad -remove%(force)s%(username)s%(password)s%(localuser)s%(localpassword)s' % {
			'force':' -force' if force else None,
			'username':' -username "%s"' % username if username else None,
			'password':' -password "%s"' % password if password else None,
			'localuser':' -localuser "%s"' % localuser if localuser else None,
			'localpassword':' -localpassword "%s"' % localpassword if localpassword else None,
		}
	)

	ret['changes']['diff'] = ''.join(difflib.unified_diff(before, show()))
	ret['comment'] = ('dsconfigad: %s\nPID: %s; RetCode: %s\n%s' % (res['stdout'], res['pid'], res['retcode'], res['stderr']))

	if res['retcode'] != 0:
		ret['result'] = False
		return ret

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
	
	if type(format) is bool and not format:
		return __salt__['cmd.run'](
			'dsconfigad -show'
		)
	elif format == 'xml':
		return __salt__['cmd.run'](
			'dsconfigad -show -xml'
		)
	else:
		return False
