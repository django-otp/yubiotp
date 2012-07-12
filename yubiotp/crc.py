"""
CRC16 implementation for Yubico OTP.
"""

def crc16(data):
    """
    Generate the crc-16 value for a byte string.

    >>> from binascii import unhexlify
    >>> c = crc16(unhexlify('8792ebfe26cc130030c20011c89f'))
    >>> hex(~c & 0xffff)
    '0xc823'
    >>> v = crc16(unhexlify('8792ebfe26cc130030c20011c89f23c8'))
    >>> hex(v)
    '0xf0b8'
    """
    crc = 0xffff

    for byte in data:
        crc ^= ord(byte)

        for i in xrange(8):
            lsb = crc & 1
            crc >>= 1
            if lsb == 1:
                crc ^= 0x8408

    return crc

def verify_crc16(data):
    """
    Return true if this given byte string has a valid crc-16 residual.

    >>> from binascii import unhexlify
    >>> verify_crc16(unhexlify('8792ebfe26cc130030c20011c89f23c8'))
    True
    >>> verify_crc16(unhexlify('0792ebfe26cc130030c20011c89f23c8'))
    False
    """
    return crc16(data) == 0xf0b8
