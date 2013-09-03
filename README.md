# dsconfigad

A module to wrap [dsconfigad](http://bit.ly/15gnT5I) calls.  This file would go in the _modules directory, [as decribed in the saltstack docs](http://bit.ly/19X3Y4c).

* add
* config
* is_set
* remove
* show

### Known Issues

This module doesn't talk properly with the salt api yet.  I get the following errors:

* The state "dsconfigad.add" in sls apps.dsconfigad is not formed as a list
* The state "dsconfigad.config" in sls apps.dsconfigad is not formed as a list

Not sure what needs to be formed as a list yet, but I'll get it figure out eventually.
