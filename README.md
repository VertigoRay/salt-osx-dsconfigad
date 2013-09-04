# dsconfigad

A module to wrap [dsconfigad](http://bit.ly/15gnT5I) calls.  This file would go in the _modules directory, [as decribed in the saltstack docs](http://bit.ly/19X3Y4c).

Public Functions:
* [add](#add)
* [config](#config)
* [remove](#remove)
* [show](#show)

Note:  The `test` function, if available, does nothing with dsconfigad.  It was used while debugging, and will likely be removed in a future commit.

Note:  The `_is_set` function is private because salt CLI passes private variables (ie: __pub_user, __pub_arg, __pub_fun, etc.) into kwargs that aren't currently handled -- and may never be.

Additional Documentation
* [Pillar](#pillar)
  * [domain](#pillar_domain)
  * [forest](#pillar_forest)
  * [computer](#pillar_computer)
  * [ou](#pillar_ou)
  * [username](#pillar_username)
  * [password](#pillar_password)
  * [localuser](#pillar_localuser)
  * [localpassword](#pillar_localpassword)
  * [init_u](#pillar_init_u)
  * [init_p](#pillar_init_p)
  * [init_lu](#pillar_init_lu)
  * [init_lp](#pillar_init_lp)
  * [alldomains](#pillar_alldomains)
  * [authority](#pillar_authority)
  * [ggid](#pillar_ggid)
  * [gid](#pillar_gid)
  * [groups](#pillar_groups)
  * [mobile](#pillar_mobile)
  * [mobileconfirm](#pillar_mobileconfirm)
  * [namespace](#pillar_namespace)
  * [localhome](#pillar_localhome)
  * [packetencrypt](#pillar_packetencrypt)
  * [packetsign](#pillar_packetsign)
  * [passinterval](#pillar_passinterval)
  * [preferred](#pillar_preferred)
  * [protocol](#pillar_protocol)
  * [restrictddns](#pillar_restrictddns)
  * [sharepoint](#pillar_sharepoint)
  * [shell](#pillar_shell)
  * [uid](#pillar_uid)
  * [useuncpath](#pillar_useuncpath)
  * [Sample Pillar](#samplepillar)
* [Good Security Practices](#goodsecuritypractices)
* [Known Issues](#knownissues)

-------------------------
<a name="add"/>
### add

Add the computer to the domain

kwargs:
* domain *: fully qualified DNS name of Active Directory Domain
* ou *: (CN=Computers) fully qualified LDAP DN of container for the computer
* force: (True) force the process (i.e., join the existing account)
* forest *: fully qualified DNS name of Active Directory Forest
* username *: username of a priveleged network user
* password *: password of a priveleged network user
* localuser *: username of a priveleged local user
* localpassword *: username of a priveleged local user
* computer *: (hostname) name of computer to add to domain

_Note:_ * will look in pillar[dsconfigad] if not provided

CLI Example (dot (.) represents the targetted computer and is NOT salt syntax):
```bash
salt '.' dsconfigad.add
```

<a name="config"/>
### config

Configure advanced options

* use_pillar    (False) apply all advanced options from pillar[dsconfigad]
  * if set, all kwargs are ignored
  * if len(kwargs) == 0: use_pillar = True

kwargs:
* localuser *: username of a priveleged local user
* localpassword *: username of a priveleged local user
* mobile: mobile user accounts for offline use
* mobileconfig: warning for mobile account creation 
* localhome: force home directory to local drive
* useuncpath: use Windows UNC for network home
* protocol: changes protocol used when mounting home
* shell: (/bin/bash) specify a default shell
* uid: name of attribute to be used for UNIX uid field
* gid: name of attribute to be used for UNIX gid field
* ggid: name of attribute to be used for UNIX group gid field
* authority: generation of Kerberos authority
* preferred: fully-qualified domain name of preferred server to query
* groups: list of groups that are granted Admin privelages on local workstation
* alldomains: allow authentication from any domain
* packetsign: config packet signing
* packetencrypt: config packet encryption
* namespace: where forest qualifies all usernames
* passinterval: how oftern to change computer trust account password, in days
* restrictddns: list of interfaces to restrict DDNS to (en0, en1, etc.)

_Note:_ * will look in pillar[dsconfigad] if not provided 

CLI Example (dot (.) represents the targetted computer and is NOT salt syntax):
```bash
salt '.' dsconfigad.config
salt '.' dsconfigad.config mobile=True
```

<a name="remove"/>
### remove

Remove the computer from domain

kwargs:
* force *: (True) force the process (i.e., join the existing account)
* username *: rname of a priveleged network user
* password *: password of a priveleged network user
* localuser *: username of a priveleged local user
* localpassword: * username of a priveleged local user

_Note:_ * will look in pillar[dsconfigad] if not provide: 

CLI Example (dot (.) represents the targetted computer and is NOT salt syntax):
```bash
salt '.' dsconfigad.remove
```

<a name="show"/>
### show

Show current configuration for Active Directory

CLI Example (dot (.) represents the targetted computer and is NOT salt syntax):
```bash
salt '.' dsconfigad.show
salt '.' dsconfigad.show xml
```

<a name="pillar"/>
### Pillar

> Pillar is an interface for Salt designed to offer global values that can be distributed to all minions. Pillar data is managed in a similar way as the Salt State Tree.

~ [Pillar Documentation](http://docs.saltstack.com/topics/pillar/) - More info on the usage of Pillars can be found there.

In this section, I'll breakdown how to YAMLize your dsconfigad settings.  A full [sample pillar](#samplepillar) .sls is available below.  Details on what each setting does can be found in [Apple's Ducumentation](http://bit.ly/15gnT5I).

**_Note:_ in Pillar, always use ALL _lowercase_!**

* [domain](#pillar_domain)
* [forest](#pillar_forest)
* [computer](#pillar_computer)
* [ou](#pillar_ou)
* [username](#pillar_username)
* [password](#pillar_password)
* [localuser](#pillar_localuser)
* [localpassword](#pillar_localpassword)
* [init_u](#pillar_init_u)
* [init_p](#pillar_init_p)
* [init_lu](#pillar_init_lu)
* [init_lp](#pillar_init_lp)

**Advanced Options:**

* [alldomains](#pillar_alldomains)
* [authority](#pillar_authority)
* [ggid](#pillar_ggid)
* [gid](#pillar_gid)
* [groups](#pillar_groups)
* [mobile](#pillar_mobile)
* [mobileconfirm](#pillar_mobileconfirm)
* [namespace](#pillar_namespace)
* [localhome](#pillar_localhome)
* [packetencrypt](#pillar_packetencrypt)
* [packetsign](#pillar_packetsign)
* [passinterval](#pillar_passinterval)
* [preferred](#pillar_preferred)
* [protocol](#pillar_protocol)
* [restrictddns](#pillar_restrictddns)
* [sharepoint](#pillar_sharepoint)
* [shell](#pillar_shell)
* [uid](#pillar_uid)
* [useuncpath](#pillar_useuncpath)

**_Note:_** These options are what's available in OS X 10.8.4.  New _Advanced Options_ that are released in future _should_ just work -- if you use them as described in the documentation.  Just use it in the same fashion as a similar option.  For example, if you want to disable a _newoption_ that has enable/disable as possible options:
```yaml
dsconfigad:
  newoption: False
```

<a name="pillar_domain"/>
#### domain

Fully qualified DNS name of Active Directory Domain.

If `salt '.' dsconfigad.show` returns an _Active Directory Domain_ that is different from this setting, the following actions are taken (dot (.) represents the targetted computer and is NOT salt syntax):

1. `salt '.' dsconfigad.remove`
2. `salt '.' dsconfigad.add`

```yaml
dsconfigad:
  domain: example.com
```

<a name="pillar_forest"/>
#### forest

Fully qualified DNS name of Active Directory Forest.

If `salt '.' dsconfigad.show` returns an _Active Directory Forest_ that is different from this setting, the following actions are taken (dot (.) represents the targetted computer and is NOT salt syntax):

1. `salt '.' dsconfigad.remove`
2. `salt '.' dsconfigad.add`

Note:  Computers are bound to the domain.  The forest is inherited.

```yaml
dsconfigad:
  forest: forest.example.com
```

<a name="pillar_computer"/>
#### computer

The Computer Account.  **This setting should not be used in most cases.**  When not used, the current hostname is used -- as detected by python's socket module.  Check your hostname with python:

```python
>>> import socket
>>> socket.gethostname()
'testcomp001'
```

If `salt '.' dsconfigad.show` returns an _Active Directory Forest_ that is different from this setting, the following actions are taken (dot (.) represents the targetted computer and is NOT salt syntax):

1. `salt '.' dsconfigad.remove`
2. `salt '.' dsconfigad.add`

```yaml
dsconfigad:
  computer: testcomp001
```

<a name="pillar_ou"/>
#### ou

Fully qualified LDAP DN of container for the computer (defaults to OU=Computers).

```yaml
dsconfigad:
  ou: 'OU=Darwin,OU=Computers,DC=example,DC=com'
```

<a name="pillar_username"/>
#### username

The username of a privileged network user.

**_Note:_ It is not recommended that you store a domain username in plain text in your Pillar.  See [init_u](#pillar_init_u) instead.**

```yaml
dsconfigad:
  username: TestUser
```

<a name="pillar_password"/>
#### password

The password of a privileged network user.

**_Note:_ It is not recommended that you store a domain password in plain text in your Pillar.  See [init_p](#pillar_init_p) instead.**

```yaml
dsconfigad:
  password: T3$t P@$$w0rd!!1
```

<a name="pillar_localuser"/>
#### localuser

The username of a privileged local user.

**_Note:_ It is not recommended that you store a local username in plain text in your Pillar.  See [init_lu](#pillar_init_lu) instead.**

**_Note:_ Since salt runs as root, this option is NOT necessary -- at least not in my testing.  However, I made it available because I don't know your use case.**

```yaml
dsconfigad:
  localuser: LocalUser
```

<a name="pillar_localpassword"/>
#### localpassword

The password of a privileged local user.

**_Note:_ It is not recommended that you store a local username in plain text in your Pillar.  See [init_lp](#pillar_init_lp) instead.**

**_Note:_ Since salt runs as root, this option is NOT necessary -- at least not in my testing.  However, I made it available because I don't know your use case.**

```yaml
dsconfigad:
  localpassword: T3$t Pa$$wOrd!!1
```

<a name="pillar_init_u"/>
#### init_u

The base64 encoded username of a privileged network user.  [Good Security Practices](#goodsecuritypractices) are recommended for this account.

**_Note:_ Base64 is _NOT_ encrypted.  It is merely obfuscated.  I am not aware of a crypto module available to a clean python install.  If you have a better way, feel free to contribute.**

To get the encoded version of your username, pass it through `base64.b64encode()` as shown:
```python
>>> import base64
>>> base64.b64encode('TestUser')
'VGVzdFVzZXI='
```

Then supply the returned value in your Pillar:
```yaml
dsconfigad:
  init_u: VGVzdFVzZXI=
```

<a name="pillar_init_p"/>
#### init_p

The base64 encoded password of a privileged network user.  [Good Security Practices](#goodsecuritypractices) are recommended for this account.

**_Note:_ Base64 is _NOT_ encrypted.  It is merely obfuscated.  I am not aware of a crypto module available to a clean python install.  If you have a better way, feel free to contribute.**

To get the encoded version of your username, pass it through `base64.b64encode()` as shown:
```python
>>> import base64
>>> base64.b64encode('T3$t P@$$w0rd!!1')
'VDMkdCBQQCQkdzByZCEhMQ=='
```

Then supply the returned value in your Pillar:
```yaml
dsconfigad:
  init_p: VDMkdCBQQCQkdzByZCEhMQ==
```

<a name="pillar_init_lu"/>
#### init_lu

The base64 encoded username of a privileged local user.

**_Note:_ Base64 is _NOT_ encrypted.  It is merely obfuscated.  I am not aware of a crypto module available to a clean python install.  If you have a better way, feel free to contribute.**

**_Note:_ Since salt runs as root, this option is NOT necessary -- at least not in my testing.  However, I made it available because I don't know your use case.**

To get the encoded version of your username, pass it through `base64.b64encode()` as shown:
```python
>>> import base64
>>> base64.b64encode('LocalUser')
'TG9jYWxVc2Vy'
```

Then supply the returned value in your Pillar:
```yaml
dsconfigad:
  init_lu: TG9jYWxVc2Vy
```

<a name="pillar_init_lp"/>
#### init_lp

The base64 encoded password of a privileged local user.

**_Note:_ Base64 is _NOT_ encrypted.  It is merely obfuscated.  I am not aware of a crypto module available to a clean python install.  If you have a better way, feel free to contribute.**

**_Note:_ Since salt runs as root, this option is NOT necessary -- at least not in my testing.  However, I made it available because I don't know your use case.**

To get the encoded version of your username, pass it through `base64.b64encode()` as shown:
```python
>>> import base64
>>> base64.b64encode('T3$t Pa$$wOrd!!1')
'VDMkdCBQYSQkd09yZCEhMQ=='
```

Then supply the returned value in your Pillar:
```yaml
dsconfigad:
  init_lp: VDMkdCBQYSQkd09yZCEhMQ==
```

<a name="pillar_alldomains"/>
#### alldomains

Enable/Disable items are _always_ set with True/False.

Enable:
```yaml
dsconfigad:
  alldomains: True
```

Disable:
```yaml
dsconfigad:
  alldomains: False
```

<a name="pillar_authority"/>
#### authority

Since, this setting isn't listed in the [Apple Docs](http://bit.ly/15gnT5I), here's the excerpt from `dsconfig --help`:
> Advanced Options - Mappings:
* authority value
 * enable or disable generation of Kerberos authority

Enable/Disable items are _always_ set with True/False.

Enable:
```yaml
dsconfigad:
  authority: True
```

Disable:
```yaml
dsconfigad:
  authority: False
```

<a name="pillar_ggid"/>
#### ggid

This setting has a -no variant.  The -no variant is used to disable the option.  Use False to disable the setting.

Disable:
```yaml
dsconfigad:
  ggid: False
```

Set ggid to the AD User Account's UnixGGID Property:
```yaml
dsconfigad:
  ggid: UnixGGID
```

<a name="pillar_gid"/>
#### gid

This setting has a -no variant.  The -no variant is used to disable the option.  Use False to disable the setting.

Disable:
```yaml
dsconfigad:
  gid: False
```

Set ggid to the AD User Account's UnixGID Property:
```yaml
dsconfigad:
  gid:  UnixGID
```

<a name="pillar_groups"/>
#### groups

This setting has a -no variant.  The -no variant is used to disable the option.  Use False to disable the setting.

Disable:
```yaml
dsconfigad:
  groups: False
```

Set Local Admin:
```yaml
dsconfigad:
  groups: EXAMPLE\DarwinAdmins
```

Set Multiple Local Admin:
```yaml
dsconfigad:
  groups:
    - EXAMPLE\DarwinAdmins
    - EXAMPLE\Domain Admins
```

<a name="pillar_mobile"/>
#### mobile

Enable/Disable items are _always_ set with True/False.

Enable:
```yaml
dsconfigad:
  mobile: True
```

Disable:
```yaml
dsconfigad:
  mobile: False
```

<a name="pillar_mobileconfirm"/>
#### mobileconfirm

Enable/Disable items are _always_ set with True/False.

Enable:
```yaml
dsconfigad:
  mobileconfirm: True
```

Disable:
```yaml
dsconfigad:
  mobileconfirm: False
```

<a name="pillar_namespace"/>
#### namespace

Using an option other than those specified in the [Apple Docs](http://bit.ly/15gnT5I) may cause unforeseen errors.

Allow login from any account in the forest:
```yaml
dsconfigad:
  namespace: forest
```

<a name="pillar_localhome"/>
#### localhome

Enable/Disable items are _always_ set with True/False.

Enable:
```yaml
dsconfigad:
  localhome: True
```

Disable:
```yaml
dsconfigad:
  localhome: False
```

<a name="pillar_packetencrypt"/>
#### packetencrypt

Using an option other than those specified in the [Apple Docs](http://bit.ly/15gnT5I) may cause unforeseen errors.

Set to ssl:
```yaml
dsconfigad:
  packetencrypt: ssl
```

<a name="pillar_packetsign"/>
#### packetsign

Using an option other than those specified in the [Apple Docs](http://bit.ly/15gnT5I) may cause unforeseen errors.

Set to require:
```yaml
dsconfigad:
  packetsign: require
```

<a name="pillar_passinterval"/>
#### passinterval

Since, at the time of this writing, this setting is compressed with the *packetsign* setting in the [Apple Docs](http://bit.ly/15gnT5I), here's the excerpt from `dsconfig --help`:
> Advanced Options - Administrative:
* passinterval days
 * how often to change computer trust account password in days _(default: 14)_

Adjust to 30 days:
```yaml
dsconfigad:
  passinterval: 30
```

<a name="pillar_preferred"/>
#### preferred

This setting has a -no variant.  The -no variant is used to disable the option.  Use False to disable the setting.

Disable:
```yaml
dsconfigad:
  preferred: False
```

Set preferred DC:
```yaml
dsconfigad:
  preferred: dc01.example.com
```

<a name="pillar_protocol"/>
#### protocol

Using an option other than those specified in the [Apple Docs](http://bit.ly/15gnT5I) may cause unforeseen errors.

Use NFS:
```yaml
dsconfigad:
  protocol: nfs
```

<a name="pillar_restrictddns"/>
#### restrictddns

From [Apple Docs](http://bit.ly/15gnT5I):
> Restricts Dynamic DNS updates to specific interfaces (e.g., en0, en1, en2, etc.).  To disable restrictions pass "" as the list.

To **disable** restrictions, use False:
```yaml
dsconfigad:
  restrictddns: False
```

To restrict to **one interface**, use a string:
```yaml
dsconfigad:
  restrictddns: en0
```

To restrict to **_one or_ more interface**, use a list:
```yaml
dsconfigad:
  restrictddns:
    - en0
    - en1
```
_Note:_ You should use a string for one interface, but a single item list _should_ work.

<a name="pillar_sharepoint"/>
#### sharepoint

Enable/Disable items are _always_ set with True/False.

Enable:
```yaml
dsconfigad:
  sharepoint: True
```

Disable:
```yaml
dsconfigad:
  sharepoint: False
```

<a name="pillar_shell"/>
#### shell

Using an option other than those specified in the [Apple Docs](http://bit.ly/15gnT5I) may cause unforeseen errors.

Use ZSH:
```yaml
dsconfigad:
  shell: /bin/zsh
```

<a name="pillar_uid"/>
#### uid

This setting has a -no variant.  The -no variant is used to disable the option.  Use False to disable the setting.

Disable:
```yaml
dsconfigad:
  uid: False
```

Set uid to the AD User Account's SID property:
```yaml
dsconfigad:
  uid: SID
```

<a name="pillar_useuncpath"/>
#### useuncpath

Enable/Disable items are _always_ set with True/False.

Enable:
```yaml
dsconfigad:
  useuncpath: True
```

Disable:
```yaml
dsconfigad:
  useuncpath: False
```

<a name="samplepillar"/>
#### Sample Pillar

pillar_roots/dsconfigad.sls:
```yaml
dsconfigad:
  init_u: VGVzdFVzZXI=
  init_p: VDMkdCBQQCQkdzByZCEhMQ==
  domain: example.com
  ou: 'OU=Darwin,OU=Computers,DC=example,DC=com'
  mobile: True
  mobileconfirm: False
  localhome: True
  sharepoint: True
  useuncpath: False
  protocol: smb
  shell: /bin/bash
  uid: SID
  gid: False
  ggid: False
  authority: True
  preferred: dc01.example.com
  groups: EXAMPLE\Domain Admins
  alldomains: True
  packetsign: allow
  packetencrypt: allow
  passinterval: 14
  restrictddns: False
  namespace: domain
```

<a name="goodsecuritypractices"/>
### Good Security Practices

When scripting services that require a password to be stored on multiple computers, you should always lock down the account so that it is only able to perform the task that you desire.  I highly suggest one account per task.

This is [discussed on TechNET](http://bit.ly/15BPePN) -- albeit not very thoroughly.  Maybe I'll blog the details later and link it here ...

<a name="knownissues"/>
### Known Issues

#### Salt API Issue

This module doesn't talk properly with the salt api yet.  I get the following errors when running `salt '*' state.highstate`:

* The state "dsconfigad.add" in sls apps.dsconfigad is not formed as a list
* The state "dsconfigad.config" in sls apps.dsconfigad is not formed as a list

Not sure what needs to be formed as a list yet, but I'll get it figure out.

#### Preferred is required

In my environment, the `preferred` option is required to bind.  I've tried to trace down the root cause of this, but with no luck.  This appears to be a _dsconfigad_ issue.

Without `preferred`, I would get the following error:

> Authentication server could not be contacted

This error is discussed on [Apple Support](https://discussions.apple.com/thread/3198558).

_Note:_ my `_ldap._tcp.example.com` record is set-up correctly.
_Note:_ using the FQDN for the domain doesn't work for `preferred`.  I get a different error about the DC not being reachable.  Only an FQDN of the server will work for `preferred`.
