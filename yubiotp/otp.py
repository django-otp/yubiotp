"""
Implementation of the Yubico OTP algorithm. This can generate and parse OTP
structures.
"""

from binascii import hexlify
from datetime import datetime
from random import randrange
from struct import pack, unpack

from .crc import crc16, verify_crc16
from .modhex import modhex, unmodhex

from Crypto.Cipher import AES


__all__ = ['parse', 'OTP', 'YubiKey', 'CRCError']


class CRCError(ValueError):
    """
    Raised when a decrypted token has an invalid checksum.
    """
    pass


def parse(token, key):
    """
    Parses a modhex-encoded Yubico OTP value and returns the public ID and the
    unpacked OTP object.

    token
        A modhex-encoded buffer. Decoded, this should consist of 0-16 bytes of
        public ID followed by 16 bytes of encrypted OTP data.
    key
        A 16-byte AES key as a binary string.

    Returns ``(identity, otp)``. ``identity`` is the public identity as a
    decoded byte string and ``otp`` is an instance of :class:`OTP`.

    Exceptions:
        - ValueError if the string can not be decoded.
        - :exc:`CRCError` if the checksum on the decrypted data is incorrect.
    """
    if len(key) != 16:
        raise ValueError('Key must be exactly 16 bytes')

    buf = unmodhex(token)
    id_len = len(buf) - 16

    identity = buf[:id_len]

    buf = buf[id_len:]
    buf = AES.new(key, AES.MODE_ECB).decrypt(buf)
    otp = OTP.unpack(buf)

    return (identity, otp)


class OTP(object):
    """
    A single YubiKey OTP. This is typically instantiated by parsing an encoded
    OTP.

    .. attribute:: uid

        The private ID. This should be a string of up to six bytes. The string
        will be right-padded with zeros if necessary.

    .. attribute:: session

        The non-volatile usage counter.

    .. attribute:: timestamp

        An integer in ``[0..2^24]``.

    .. attribute:: counter

        The volatile usage counter.

    .. attribute:: rand

        An arbitrary number in ``[0..2^16]``.
    """
    def __init__(self, uid, session, timestamp, counter, rand):
        self.uid = uid
        self.session = session
        self.timestamp = timestamp
        self.counter = counter
        self.rand = rand

    def __repr__(self):
        return 'OTP: 0x{0} {1}/{2} ({3}/{4})'.format(
            hexlify(self.uid),
            self.session, self.counter,
            hex(self.timestamp), hex(self.rand)
        )

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
            self.uid,
            self.session,
            self.timestamp & 0xff,
            (self.timestamp >> 8) & 0xff,
            (self.timestamp >> 16) & 0xff,
            self.counter,
            self.rand,
        )

        buf = pack('<6sH3BBH', *fields)

        crc = ~crc16(buf) & 0xffff
        buf += pack('<H', crc)

        return buf

    @classmethod
    def unpack(cls, buf):
        """
        Parse a packed OTP. This is the complement to :meth:`pack` so the
        buffer should be a decoded, decrypted OTP buffer. Raises
        :exc:`CRCError` if the buffer does not pass crc validation.
        """
        if not verify_crc16(buf):
            raise CRCError('OTP checksum is invalid')

        uid, session, t1, t2, t3, counter, rand, crc = unpack('<6sH3BBHH', buf)

        timestamp = (t3 << 16) | (t2 << 8) | (t1)

        return cls(uid, session, timestamp, counter, rand)


class YubiKey(object):
    """
    A simulated YubiKey device. This can be used to generate a sequence of
    Yubico OTP passwords.

    .. attribute:: key

        An AES key as a binary string.

    .. attribute:: uid

        The private ID. This should be a string of up to six bytes. The string
        will be right-padded with zeros if necessary.

    .. attribute:: session

        The non-volatile usage counter. It is the caller's responsibility to
        persist this. Note that this may increment if the volatile counter
        wraps, so you should only increment and persist this after you have
        finished generating tokens.

    .. attribute:: counter

        The volatile session counter. This defaults to 0 at init time, but the
        caller can override this.

    .. attribute:: public_id

        An optional public id to identify generated passwords. This will be
        truncated to 16 bytes.
    """
    def __init__(self, key, uid, session, counter=0, public_id=''):
        if len(key) != 16:
            raise ValueError('key must be exactly 16 bytes')

        self.key = key
        self.uid = uid
        self.session = session if (session < 0x7fff) else 0x7fff
        self.counter = counter
        self.public_id = public_id[:16]

        self._init_timestamp()

    def generate(self):
        """
        Generate a YubiKey token. This simluates pressing the YubiKey button
        and returns the encoded token.
        """
        otp = OTP(self.uid, self.session, self._timestamp(), self.counter, randrange(0xffff))
        self._increment_counter()

        buf = AES.new(self.key, mode=AES.MODE_ECB).encrypt(otp.pack())

        return modhex(self.public_id + buf)

    def _init_timestamp(self, timestamp):
        self._timestamp_base = randrange(0xffffff)
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
        if self.counter == 0xff:
            self._increment_session()
            self.counter = 0
        else:
            self.counter += 1

    def _increment_session(self):
        self.session = min(self.session + 1, 0x7fff)
