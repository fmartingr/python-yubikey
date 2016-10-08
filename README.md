python-yubikey
==============

A simple wrapper to use your yubikey with the yubico API.


## Install the lib

```
pip install python-yubikey
```


## Register for an API key

``` python
from yubikey import Yubikey

yubi = Yubikey()
yubi.register('<EMAIL>', '<INSERT OTP HERE>')
# yubi.id and yubi.key are now set
```

## Check valid OTP

``` python
yubi = Yubikey('<ID>', '<Key>')
result = yubi.verify('<INSERT ANOHTER OTP HERE>')
# True / False
# If <key> is provided, requests will be signed and the responses checked.
```

## Optionals

``` python
# Using custom API server
# Must be one of YubicoWS._servers
yubi = Yubikey(123, 'dGhpc3JlcG9yb2Nrcw==', server='api2.yubico.com')

# Using http instead of https
yubi = Yubikey(123, 'dGhpc3JlcG9yb2Nrcw==', protocol='http')
```

# NO WARRANTY
THE PROGRAM IS DISTRIBUTED IN THE HOPE THAT IT WILL BE USEFUL, BUT WITHOUT ANY WARRANTY. IT IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION.

IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW THE AUTHOR WILL BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
