Validation Client
=================

.. automodule:: yubiotp.client


Protocol Version 2.0
--------------------

.. autoclass:: YubiClient20
    :members: verify, url


Protocol Version 1.1
--------------------

.. autoclass:: YubiClient11
    :members: verify, url


Protocol Version 1.0
--------------------

.. autoclass:: YubiClient10
    :members: verify, url


Response
--------

.. autoclass:: YubiResponse
    :members: is_ok, status, is_valid, is_signature_valid, is_token_valid,
        is_nonce_valid, public_id
