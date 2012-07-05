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


class CRCError(ValueError):
    pass


class OTPDevice(object):
    """
    A simulated Yubico OTP device. This can be used to generate a sequence of
    Yubikey OTP passwords.
    """
    def __init__(self, key, uid, session, counter=0, public_id=''):
        """
        key: An AES key.
        uid: The private ID. This should be a string of up to six bytes. The
            string will be right-padded with zeros if necessary.
        session: The non-volatile usage counter. It is the caller's
            responsibility to persist this. Note that this may increment if the
            volatile counter wraps, so the correct way to handle this is to
            store self.session + 1 after you've finished generating passwords.
        counter: The volatile session counter. This defaults to 0 at init time,
            but the caller can override this.
        public_id: An optional public id to identify generated passwords. This
            will be truncated to 16 bytes.
        """
        if len(key) != 16:
            raise ValueError('key must be exactly 16 bytes')

        self.key = key
        self.uid = uid
        self.session = session if (session < 0x7fff) else 0x7fff
        self.counter = counter
        self.public_id = public_id[:16]

        self._init_timestamp()

    def generate(self):
        otp = OTP(self.uid, self.session, self._timestamp(), self.counter, randrange(0xffff))
        buf = AES.new(self.key, mode=AES.MODE_ECB).encrypt(otp.pack())

        self._increment_counter()

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


class OTP(object):
    """
    A single YubiKey OTP. This is typically instantiated by parsing and encoded
    OTP.
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
        Parse a packed OTP. This is the complement to pack(), so the buffer
        should be a decoded, decrypted OTP buffer. This returns None if the
        buffer does not pass crc validation.
        """
        if not verify_crc16(buf):
            return None

        uid, session, t1, t2, t3, counter, rand, crc = unpack('<6sH3BBHH', buf)

        timestamp = (t3 << 16) | (t2 << 8) | (t1)

        return cls(uid, session, timestamp, counter, rand)


def parse(encoded, key):
    """
    Parses a modhex-encoded Yubico OTP value and returns the public ID and the
    unpacked OTP object.

    encoded: a modhex-encoded buffer. Decoded, this should consist of 0-16
        bytes of public ID followed by 16 bytes of encrypted OTP data.
    key: a 16-byte AES key.

    returns: (identity, otp). identity is a decoded byte string and otp is an
        instance of OTP.

    raises: ValueError if the string can not be decoded.
            CRCError if the checksum on the decrypted data is incorrect.
    """
    if len(key) != 16:
        raise ValueError('Key must be exactly 16 bytes')

    buf = unmodhex(encoded)

    pub_len = len(buf) - 16
    identity = buf[:pub_len]
    buf = buf[pub_len:]

    buf = AES.new(key, AES.MODE_ECB).decrypt(buf)
    if not verify_crc16(buf):
        raise CRCError('OTP checksum is invalid')

    otp = OTP.unpack(buf)

    return (identity, otp)
