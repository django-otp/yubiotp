"""
Implementation of the Yubico OTP algorithm. This can generate and parse OTP
structures.

>>> key = '0123456789abcdef'
>>> otp = OTP(0xba9876543210, 5, 0x0153f8, 0, 0x1234)
>>> token = encode_otp(otp, key, 'mypublicid')
>>> token
'htikicighdhrhkhehkhfefnijnthcvncrgbrrklcfrhndchilifi'
>>> public_id, otp2 = decode_otp(token, key)
>>> public_id
'mypublicid'
>>> otp2 == otp
True
"""

from datetime import datetime
from random import randrange
from struct import pack, unpack

from .crc import crc16, verify_crc16
from .modhex import modhex, unmodhex

from Crypto.Cipher import AES


__all__ = ['decode_otp', 'encode_otp', 'OTP', 'YubiKey', 'CRCError']


class CRCError(ValueError):
    """
    Raised when a decrypted token has an invalid checksum.
    """
    pass


def decode_otp(token, key):
    """
    Decodes a modhex-encoded Yubico OTP value and returns the public ID and the
    unpacked :class:`OTP` object.

    :param str token: A modhex-encoded buffer. Decoded, this should consist of
        0-16 bytes of public ID followed by 16 bytes of encrypted OTP data.
    :param str key: A 16-byte AES key as a binary string.

    :returns: The public ID as a decoded string and the OTP structure.
    :rtype: (str, :class:`OTP`)

    :raises: ``ValueError`` if the string can not be decoded.
    :raises: :exc:`CRCError` if the checksum on the decrypted data is
        incorrect.
    """
    if len(key) != 16:
        raise ValueError('Key must be exactly 16 bytes')

    buf = unmodhex(token)
    public_id, buf = buf[:-16], buf[-16:]
    buf = AES.new(key, AES.MODE_ECB).decrypt(buf)
    otp = OTP.unpack(buf)

    return (public_id, otp)


def encode_otp(otp, key, public_id=''):
    """
    Encodes an :class:`OTP` structure, encrypts it with the given key and
    returns the modhex-encoded token.

    :param otp: The OTP structure.
    :type otp: :class:`OTP`

    :param str key: A 16-byte AES key as a binary string.
    :param str public_id: An optional public id. This will be truncated to 16
        bytes.
    """
    if len(key) != 16:
        raise ValueError('Key must be exactly 16 bytes')

    buf = otp.pack()
    buf = AES.new(key, AES.MODE_ECB).encrypt(buf)
    buf = public_id[:16] + buf
    token = modhex(buf)

    return token


def public_id(token):
    """
    Returns the fully decoded public ID from an otp token.

    :param str token: A monhex-encoded YubiKey OTP token.

    :returns: The public ID as a fully decoded string.
    :rtype: str
    """
    return unmodhex(token[:-32])


class OTP(object):
    """
    A single YubiKey OTP. This is typically instantiated by parsing an encoded
    OTP.

    :param int uid: The private ID in [0..2^48].
    :param int session: The non-volatile usage counter.
    :param int timestamp: An integer in ``[0..2^24]``.
    :param int counter: The volatile usage counter.
    :param int rand: An arbitrary number in ``[0..2^16]``.
    """
    def __init__(self, uid, session, timestamp, counter, rand):
        self.uid = uid
        self.session = session
        self.timestamp = timestamp
        self.counter = counter
        self.rand = rand

    def __repr__(self):
        return 'OTP: 0x{0:x} {1}/{2} (0x{3:x}/0x{4:x})'.format(self.uid, self.session, self.counter, self.timestamp, self.rand)

    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return False

        self_props = (self.uid, self.session, self.timestamp, self.counter, self.rand)
        other_props = (other.uid, other.session, other.timestamp, other.counter, other.rand)

        return (self_props == other_props)

    def pack(self):
        """
        Returns the OTP packed into a binary string, ready to be encrypted and
        encoded.
        """
        fields = (
            self.uid & 0xffffffff,
            (self.uid >> 32) & 0xffff,
            self.session,
            self.timestamp & 0xff,
            (self.timestamp >> 8) & 0xff,
            (self.timestamp >> 16) & 0xff,
            self.counter,
            self.rand,
        )

        buf = pack('<IHH3BBH', *fields)

        crc = ~crc16(buf) & 0xffff
        buf += pack('<H', crc)

        return buf

    @classmethod
    def unpack(cls, buf):
        """
        Parse a packed OTP. This is the complement to :meth:`pack` so the
        buffer should be a decoded, decrypted OTP buffer.

        :param str buf: A packed OTP structure.
        :raises: :exc:`CRCError` if the buffer does not pass crc validation.
        """
        if not verify_crc16(buf):
            raise CRCError('OTP checksum is invalid')

        u1, u2, session, t1, t2, t3, counter, rand, crc = unpack('<IHH3BBHH', buf)

        uid = (u2 << 32) | u1
        timestamp = (t3 << 16) | (t2 << 8) | t1

        return cls(uid, session, timestamp, counter, rand)


class YubiKey(object):
    """
    A simulated YubiKey device. This can be used to generate a sequence of
    Yubico OTP tokens.

    :param int uid: The private ID in [0..2^48].
    :param int session: The non-volatile usage counter. It is the caller's
        responsibility to persist this. Note that this may increment if the
        volatile counter wraps, so you should only increment and persist this
        after you have finished generating tokens.
    :param int counter: The volatile session counter. This defaults to 0 at
        init time, but the caller can override this.
    """
    def __init__(self, uid, session, counter=0):
        self.uid = uid
        self.session = min(session, 0x7fff)
        self.counter = min(counter, 0xff)

        self._init_timestamp()

    def generate(self):
        """
        Return a new OTP object, as if the user had pressed the YubiKey button.

        :rtype: :class:`OTP`
        """
        otp = OTP(self.uid, self.session, self._timestamp(), self.counter, randrange(0xffff))
        self._increment_counter()

        return otp

    def _init_timestamp(self):
        self._timestamp_base = randrange(0x00ffff)
        self._timestamp_start = datetime.now()

    def _timestamp(self):
        """
        Returns the current timestamp value, based on the number of seconds
        since the object was created.
        """
        delta = datetime.now() - self._timestamp_start
        delta = delta.days * 86400 + delta.seconds

        return (self._timestamp_base + (delta * 8)) % 0xffffff

    def _increment_counter(self):
        if self.counter >= 0xff:
            self._increment_session()
            self.counter = 0
        else:
            self.counter += 1

    def _increment_session(self):
        self.session = min(self.session + 1, 0x7fff)
