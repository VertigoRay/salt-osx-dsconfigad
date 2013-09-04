# dsconfigad

A module to wrap [dsconfigad](http://bit.ly/15gnT5I) calls.

---

##Install

This is a very basic (4 steps) install walkthrough.  You will need to adjust this to your environment.  If you have salt specific questions, connected with the [SaltStack community](http://saltstack.org).

1. Place [dsconfigad.py](https://github.com/VertigoRay/salt-osx-dsconfigad/blob/master/dsconfigad.py) in the file_roots/[_modules](http://bit.ly/19X3Y4c) directory.
2. Setup the [dsconfigad Pillar](#pillar).  
  _Might want to do some testing at this point ..._  
  * `salt 'testcomp001' state.highstate`
  * `salt 'testcomp001' dsconfigad.add`
  * `salt 'testcomp001' dsconfigad.show`
  _/end testing ..._  

3. Create an file_roots/dsconfigad/init.sls:  
```yaml
dsconfigad.add
dsconfigad.config
```

4. Add dsconfigad to your top.sls -- hopefully you have a `dev` [environment](http://docs.saltstack.com/ref/states/top.html) to test with, else use `base`:  
```yaml
dev:
      '*':
        - dsconfigad
```

[Known Issues ...](#knownissues)

---

Public Functions:
* [add](#add)
* [config](#config)
* [remove](#remove)
* [show](#show)

Note:  The `test` function, if available, does nothing with dsconfigad.  It was used while debugging, and will likely be removed in a future commit.

Note:  The `_is_set` function is private because salt CLI passes private variables (ie: __pub_user, __pub_arg, __pub_fun, etc.) into kwargs that aren't currently handled -- and may never be.

Additional Documentation
* [Pillar](#pillar)
  * [domain](#domain)
  * [forest](#forest)
  * [computer](#computer)
  * [ou](#ou)
  * [username](#username)
  * [password](#password)
  * [localuser](#localuser)
  * [localpassword](#localpassword)
  * [init_u](#init_u)
  * [init_p](#init_p)
  * [init_lu](#init_lu)
  * [init_lp](#init_lp)
  * [alldomains](#alldomains)
  * [authority](#authority)
  * [ggid](#ggid)
  * [gid](#gid)
  * [groups](#groups)
  * [mobile](#mobile)
  * [mobileconfirm](#mobileconfirm)
  * [namespace](#namespace)
  * [localhome](#localhome)
  * [packetencrypt](#packetencrypt)
  * [packetsign](#packetsign)
  * [passinterval](#passinterval)
  * [preferred](#preferred)
  * [protocol](#protocol)
  * [restrictddns](#restrictddns)
  * [sharepoint](#sharepoint)
  * [shell](#shell)
  * [uid](#uid)
  * [useuncpath](#useuncpath)
  * [Sample Pillar](#samplepillar)
* [Good Security Practices](#goodsecuritypractices)
* [Known Issues](#knownissues)

---

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

### show

Show current configuration for Active Directory

CLI Example (dot (.) represents the targetted computer and is NOT salt syntax):
```bash
salt '.' dsconfigad.show
salt '.' dsconfigad.show xml
```

### Pillar

> Pillar is an interface for Salt designed to offer global values that can be distributed to all minions. Pillar data is managed in a similar way as the Salt State Tree.

~ [Pillar Documentation](http://docs.saltstack.com/topics/pillar/) - More info on the usage of Pillars can be found there.

In this section, I'll breakdown how to YAMLize your dsconfigad settings.  A full [sample pillar](#samplepillar) .sls is available below.  Details on what each setting does can be found in [Apple's Ducumentation](http://bit.ly/15gnT5I).

**_Note:_ in Pillar, always use ALL _lowercase_!**

* [domain](#domain)
* [forest](#forest)
* [computer](#computer)
* [ou](#ou)
* [username](#username)
* [password](#password)
* [localuser](#localuser)
* [localpassword](#localpassword)
* [init_u](#init_u)
* [init_p](#init_p)
* [init_lu](#init_lu)
* [init_lp](#init_lp)

**Advanced Options:**

* [alldomains](#alldomains)
* [authority](#authority)
* [ggid](#ggid)
* [gid](#gid)
* [groups](#groups)
* [mobile](#mobile)
* [mobileconfirm](#mobileconfirm)
* [namespace](#namespace)
* [localhome](#localhome)
* [packetencrypt](#packetencrypt)
* [packetsign](#packetsign)
* [passinterval](#passinterval)
* [preferred](#preferred)
* [protocol](#protocol)
* [restrictddns](#restrictddns)
* [sharepoint](#sharepoint)
* [shell](#shell)
* [uid](#uid)
* [useuncpath](#useuncpath)

**_Note:_** These options are what's available in OS X 10.8.4.  New _Advanced Options_ that are released in future _should_ just work -- if you use them as described in the documentation.  Just use it in the same fashion as a similar option.  For example, if you want to disable a _newoption_ that has enable/disable as possible options:
```yaml
dsconfigad:
  newoption: False
```

#### domain

Fully qualified DNS name of Active Directory Domain.

If `salt '.' dsconfigad.show` returns an _Active Directory Domain_ that is different from this setting, the following actions are taken (dot (.) represents the targetted computer and is NOT salt syntax):

1. `salt '.' dsconfigad.remove`
2. `salt '.' dsconfigad.add`

```yaml
dsconfigad:
  domain: example.com
```

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

#### ou

Fully qualified LDAP DN of container for the computer (defaults to OU=Computers).

```yaml
dsconfigad:
  ou: 'OU=Darwin,OU=Computers,DC=example,DC=com'
```

#### username

The username of a privileged network user.

**_Note:_ It is not recommended that you store a domain username in plain text in your Pillar.  See [init_u](#init_u) instead.**

```yaml
dsconfigad:
  username: TestUser
```

#### password

The password of a privileged network user.

**_Note:_ It is not recommended that you store a domain password in plain text in your Pillar.  See [init_p](#init_p) instead.**

```yaml
dsconfigad:
  password: T3$t P@$$w0rd!!1
```

#### localuser

The username of a privileged local user.

**_Note:_ It is not recommended that you store a local username in plain text in your Pillar.  See [init_lu](#init_lu) instead.**

**_Note:_ Since salt runs as root, this option is NOT necessary -- at least not in my testing.  However, I made it available because I don't know your use case.**

```yaml
dsconfigad:
  localuser: LocalUser
```

#### localpassword

The password of a privileged local user.

**_Note:_ It is not recommended that you store a local username in plain text in your Pillar.  See [init_lp](#init_lp) instead.**

**_Note:_ Since salt runs as root, this option is NOT necessary -- at least not in my testing.  However, I made it available because I don't know your use case.**

```yaml
dsconfigad:
  localpassword: T3$t Pa$$wOrd!!1
```

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

#### namespace

Using an option other than those specified in the [Apple Docs](http://bit.ly/15gnT5I) may cause unforeseen errors.

Allow login from any account in the forest:
```yaml
dsconfigad:
  namespace: forest
```

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

#### packetencrypt

Using an option other than those specified in the [Apple Docs](http://bit.ly/15gnT5I) may cause unforeseen errors.

Set to ssl:
```yaml
dsconfigad:
  packetencrypt: ssl
```

#### packetsign

Using an option other than those specified in the [Apple Docs](http://bit.ly/15gnT5I) may cause unforeseen errors.

Set to require:
```yaml
dsconfigad:
  packetsign: require
```

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

#### protocol

Using an option other than those specified in the [Apple Docs](http://bit.ly/15gnT5I) may cause unforeseen errors.

Use NFS:
```yaml
dsconfigad:
  protocol: nfs
```

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

#### shell

Using an option other than those specified in the [Apple Docs](http://bit.ly/15gnT5I) may cause unforeseen errors.

Use ZSH:
```yaml
dsconfigad:
  shell: /bin/zsh
```

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

#### Sample Pillar

roots/dsconfigad.sls:
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

### Good Security Practices

When scripting services that require a password to be stored on multiple computers, you should always lock down the account so that it is only able to perform the task that you desire.  I highly suggest one account per task.

This is [discussed on TechNET](http://bit.ly/15BPePN) -- albeit not very thoroughly.  Maybe I'll blog the details later and link it here ...

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
