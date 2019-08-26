.. image:: https://img.shields.io/pypi/v/yubiotp?color=blue
   :target: https://pypi.org/project/yubiotp/
   :alt: PyPI
.. image:: https://img.shields.io/readthedocs/yubiotp
   :target: https://yubiotp.readthedocs.io/
   :alt: Documentation
.. image:: https://img.shields.io/badge/github-yubiotp-green
   :target: https://github.com/django-otp/yubiotp
   :alt: Source

This is a library for verifying `YubiKey <https://www.yubico.com/>`_ OTP tokens.
It includes both the low-level implementation for verifying tokens locally and
clients for multiple versions of the Yubico validation web service. The primary
audience is developers who wish to verify YubiKey tokens in their applications,
presumably as part of a multi-factor authentication scheme.

For testing and experimenting, the included ``yubikey`` script simulates one or
more YubiKey devices using a config file. It also includes utility commands
such as a modhex converter. See ``yubikey -h`` for details.

This also includes a command-line web service client called ``yubiclient``. See
``yubiclient -h`` for details.
