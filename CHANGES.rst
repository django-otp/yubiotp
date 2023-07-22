Change Log
==========

Unreleased - Tooling
--------------------------------------------------------------------------------

This project is now managed with `hatch`_, which replaces setuptools, pipenv,
and tox. Users of the package should not be impacted. Developers can refer to
the readme for details. If you're packaging this project from source, I suggest
relying on pip's isolated builds rather than using hatch directly.

.. _hatch: https://hatch.pypa.io/


v1.0.0 - August 13, 2020 - Drop Python 2 support
-------------------------------------------------------------------------------

- Dropped support for Python 2 and removed six.


v0.2.2 - July 20, 2018 - Switch to pycryptodome
-----------------------------------------------

- Switch from the deprecated pycrypto to pycryptodome.

- Update supported Python versions.


v0.2.1 - September 10, 2013 - Python 3 compatibility
----------------------------------------------------

- Updated for Python 2/3 compatibility.


v0.2.0 - July 21, 2012 - yubiclient
-----------------------------------

- Added yubiclient, the Yubico web service client.


v0.1.0 - July 12, 2012 - Initial release
----------------------------------------

Initial release
