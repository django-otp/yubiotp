"""
Each supported protocol version is implemented by a separate class. They all
derive from :class:`YubiClient10`, which provides the shared API.
"""
from base64 import b64encode, b64decode
from hashlib import sha1
import hmac
from random import choice
from urllib import urlencode
from urllib2 import urlopen

from .modhex import unmodhex


class YubiClient10(object):
    """
    Base class for Yubico validation clients. Most users will instantiate
    :class:`YubiClient20`. This class implements protocol version 1.0.

    http://code.google.com/p/yubikey-val-server-php/wiki/ValidationProtocolV10

    :param int api_id: Your API id.
    :param str api_key: Your base64-encoded API key.
    :param bool ssl: ``True`` if we should used https URLs by default.
    """
    _NONCE_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

    def __init__(self, api_id=1, api_key=None, ssl=True):
        self.api_id = api_id
        self.api_key = api_key
        self.ssl = ssl

    def verify(self, token):
        """
        Verify a single Yubikey OTP against the validation service.

        :param str token: A modhex-encoded YubiKey OTP, as generated by a YubiKey
            device.

        :returns: A response from the validation service.
        :rtype: :class:`YubiResponse`
        """
        nonce = self.nonce()

        url = self.url(token, nonce)
        stream = urlopen(url)
        response = YubiResponse(stream.read(), self.api_key, token, nonce)
        stream.close()

        return response

    def url(self, token, nonce=None):
        """
        :param str token: A modhex-encoded YubiKey OTP, as generated by a
            YubiKey.
        :param str nonce: A nonce string, or ``None`` to generate a random one.

        :returns: The URL that we would use to validate the token.
        :rtype: str
        """
        if nonce is None:
            nonce = self.nonce()

        return '{0}?{1}'.format(self.base_url, self.param_string(token, nonce))

    _base_url = None

    def _get_base_url(self):
        if self._base_url is None:
            self._base_url = self.default_base_url()

        return self._base_url

    def _set_base_url(self, url):
        self._base_url = url

    def _del_base_url(self):
        delattr(self, '_base_url')

    #: The base URL of the validation service. Set this if you want to use a
    #: custom validation service.
    base_url = property(_get_base_url, _set_base_url, _del_base_url)

    def default_base_url(self):
        if self.ssl:
            return 'https://api.yubico.com/wsapi/verify'
        else:
            return 'http://api.yubico.com/wsapi/verify'

    def nonce(self):
        return ''.join(choice(self._NONCE_CHARS) for i in xrange(32))

    def param_string(self, token, nonce):
        params = self.params(token, nonce)

        if self.api_key is not None:
            signature = param_signature(params, self.api_key)
            params.append(('h', b64encode(signature)))

        return urlencode(params)

    def params(self, token, nonce):
        return [
            ('id', self.api_id),
            ('otp', token),
        ]


class YubiClient11(YubiClient10):
    """
    Client for the Yubico validation service, version 1.1.

    http://code.google.com/p/yubikey-val-server-php/wiki/ValidationProtocolV11

    :param int api_id: Your API id.
    :param str api_key: Your base64-encoded API key.
    :param bool ssl: ``True`` if we should used https URLs by default.
    :param bool timestamp: ``True`` if we want the server to include timestamp
        and counter information int the response.
    """
    def __init__(self, api_id=1, api_key=None, ssl=True, timestamp=False):
        super(YubiClient11, self).__init__(api_id, api_key, ssl)

        self.timestamp = timestamp

    def params(self, token, nonce):
        params = super(YubiClient11, self).params(token, nonce)

        if self.timestamp:
            params.append(('timestamp', '1'))

        return params


class YubiClient20(YubiClient11):
    """
    Client for the Yubico validation service, version 2.0.

    http://code.google.com/p/yubikey-val-server-php/wiki/ValidationProtocolV20

    :param int api_id: Your API id.
    :param str api_key: Your base64-encoded API key.
    :param bool ssl: ``True`` if we should used https URLs by default.
    :param bool timestamp: ``True`` if we want the server to include timestamp
        and counter information int the response.
    :param sl: See protocol spec.
    :param timeout: See protocol spec.
    """
    def __init__(self, api_id=1, api_key=None, ssl=True, timestamp=False, sl=None, timeout=None):
        super(YubiClient20, self).__init__(api_id, api_key, ssl, timestamp)

        self.sl = sl
        self.timeout = timeout

    def default_base_url(self):
        if self.ssl:
            return 'https://api.yubico.com/wsapi/2.0/verify'
        else:
            return 'http://api.yubico.com/wsapi/2.0/verify'

    def params(self, token, nonce):
        params = super(YubiClient20, self).params(token, nonce)

        params.append(('nonce', nonce))

        if self.sl is not None:
            params.append(('sl', self.sl))

        if self.timeout is not None:
            params.append(('timeout', self.timeout))

        return params


class YubiResponse(object):
    """
    A response from the Yubico validation service.

    .. attribute:: fields

        A dictionary of the response fields (excluding 'h').
    """
    def __init__(self, raw, api_key, token, nonce):
        self.raw = raw
        self.api_key = api_key
        self.token = token
        self.nonce = nonce

        self.fields = {}
        self.signature = None

        self._parse_response()

    def _parse_response(self):
        self.fields = dict(tuple(line.split('=', 1)) for line in self.raw.splitlines() if '=' in line)

        if 'h' in self.fields:
            self.signature = b64decode(self.fields['h'])
            del self.fields['h']

    def is_ok(self):
        """
        Returns true if all validation checks pass and the status is 'OK'.

        :rtype: bool
        """
        return all([
            self.status == 'OK',
            self.is_signature_valid() is not False,
            self.is_token_valid() is not False,
            self.is_nonce_valid() is not False,
        ])

    def status(self):
        """
        If the signature is not invalid, this returns the value of the status
        field. Otherwise, it returns the special status ``'BAD_RESPONSE'``
        """
        if self.is_signature_valid() is not False:
            return self.fields.get('status')
        else:
            return 'BAD_RESPONSE'

    def is_signature_valid(self):
        """
        Validates the response signature.

        :returns: ``True`` if the signature is valid; ``False`` if not;
            ``None`` if we don't have an api_key with which to validate it.
        """
        if self.api_key is not None:
            signature = param_signature(self.fields.items(), self.api_key)
            valid = (signature == self.signature)
        else:
            valid = None

        return valid

    def is_token_valid(self):
        """
        Validates the otp token sent in the response.

        :returns: ``True`` if the token in the response is the same as the one
            in the request; ``False`` if not; ``None`` if the response does not
            contain an token.
        """
        if 'otp' in self.fields:
            valid = self.fields['otp'] == self.token
        else:
            valid = None

        return valid

    def is_nonce_valid(self):
        """
        Validates the nonce value sent in the response.

        :returns: ``True`` if the nonce int the response is the same as the one
            in the request; ``False`` if not; ``None`` if we didn't send a
            nonce.
        """
        if self.nonce is not None:
            valid = (self.fields.get('nonce') == self.nonce)
        else:
            valid = None

        return valid

    @property
    def public_id(self):
        """
        Returns the public id of the response token as a 48-bit unsigned int.

        :returns: The fully decoded public ID portion of ``token``, if any.
        :rtype: str or ``None``.
        """
        token = self.fields.get('otp')
        public_id = unmodhex(token[:-32]) if token else None

        return public_id


def param_signature(params, api_key):
    """
    Returns the signature over a list of Yubico validation service parameters.
    Note that the signature algorithm packs the paramters into a form similar
    to URL parameters, but without any escaping.

    :param params: An association list of parameters, such as you would give to
        urllib.urlencode.
    :type params: list of 2-tuples

    :param str api_key: The Yubico API key (raw, not base64-encoded).

    :returns: The parameter signature (raw, not base64-encoded).
    :rtype: str
    """
    param_string = '&'.join('{0}={1}'.format(k,v) for k,v in sorted(params))
    signature = hmac.new(api_key, param_string, sha1).digest()

    return signature
