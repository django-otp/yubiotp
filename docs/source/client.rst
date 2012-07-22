Validation Client
=================

.. automodule:: yubiotp.client


Protocol Version 1.0
--------------------

.. autoclass:: YubiClient10
    :members: verify, url, base_url


Protocol Version 1.1
--------------------

Subclass of :class:`YubiClient10`.

.. autoclass:: YubiClient11


Protocol Version 2.0
--------------------

Subclass of :class:`YubiClient11`.

.. autoclass:: YubiClient20


Response
--------

.. autoclass:: YubiResponse
    :members: is_ok, status, is_signature_valid, is_token_valid, is_nonce_valid,
        public_id
