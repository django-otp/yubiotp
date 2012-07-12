YubiOTP
=======

This is an implementation of the Yubico OTP algorithm, used on YubiKey devices.
The primary audience is developers who wish to verify YubiKey tokens in their
applications, presumably as part of a multi-factor authentication scheme. Note
that this is *not* a YubiCloud client, it's the low-level implementation. Those
wishing to verify YubiKey tokens in their application will be most interested in
:meth:`yubiotp.otp.decode`.

For testing and experimenting, the included ``yubikey`` script simulates one or
more YubiKey devices using a config file. See the tool's help text for
documentation.


yubiotp.otp
-----------

.. automodule:: yubiotp.otp
    :members:


yubiotp.modhex
--------------

.. automodule:: yubiotp.modhex
    :members:


yubiotp.crc
-----------

.. automodule:: yubiotp.crc
    :members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

