This is an implementation of the Yubico OTP algorithm, used on YubiKey devices.
The primary audience is developers who wish to verify YubiKey tokens in their
applications, presumably as part of a multi-factor authentication scheme. Note
that this is *not* a YubiCloud client, it's the low-level implementation.

For testing and experimentation, the included ``yubiotp`` script is a
command-line interface to the OTP parsing and the ``yubikey`` script simulates
one or more YubiKey devices using a config file.
