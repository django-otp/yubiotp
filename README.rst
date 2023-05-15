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
such as a modhex converter. See ``hatch run yubikey -h`` for details.

This also includes a command-line web service client called ``yubiclient``. See
``hatch run yubiclient -h`` for details.

.. end-of-doc-intro


Development
-----------

This project is built and managed with `hatch`_. If you don't have hatch, I
recommend installing it with `pipx`_: ``pipx install hatch``.

``pyproject.toml`` defines several useful scripts for development and testing.
The default environment includes all dev and test dependencies for quickly
running tests. The ``test`` environment defines the test matrix for running the
full validation suite.

As a quick primer, hatch scripts can be run with
``hatch run [<env>:]<script>``. To run linters and tests in the default
environment, just run ``hatch run check``. This should run tests with your
default Python version. Other scripts include:

* **manage**: Run a management command via the test project. This can be used to
  generate migrations.
* **lint**: Run all linters.
* **fix**: Run all fixers to address linting issues. This may not fix every
  issue reported by lint.
* **test**: Run all tests.
* **check**: Run linters and tests.
* **warn**: Run tests with all warnings enabled. This is especially useful for
  seeing deprecation warnings in new versions of Django.
* **cov**: Run tests and print a code coverage report.

To run the full test matrix, run ``hatch run test:run``. You will need multiple
specific Python versions installed for this.

You can clean up the hatch environments with ``hatch env prune``, for example to
force dependency updates.


.. _hatch: https://hatch.pypa.io/
.. _pipx: https://pypa.github.io/pipx/
