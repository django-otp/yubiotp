"""
Implementation of modhex encoding, which uses keyboard-independent characters.

hex digit:     0123456789abcdef
modehex digit: cbdefghijklnrtuv

http://www.yubico.com/modhex-calculator
"""

from binascii import hexlify, unhexlify
from functools import partial


def modhex(data):
    """
    Encode a string as modhex.

    >>> modhex('abcdefghijklmnop')
    'hbhdhehfhghhhihjhkhlhnhrhthuhvic'
    """
    return hex_to_modhex(hexlify(data))

def unmodhex(encoded):
    """
    Decode a modhex string to its binary form.

    >>> unmodhex('hbhdhehfhghhhihjhkhlhnhrhthuhvic')
    'abcdefghijklmnop'
    >>> unmodhex('hbhdxx')
    Traceback (most recent call last):
        ...
    ValueError: Illegal modhex character in input
    """
    try:
        return unhexlify(modhex_to_hex(encoded))
    except StopIteration as e:
        raise ValueError('Illegal modhex character in input')

def hex_to_modhex(hex_str):
    """
    Convert a string of hex digits to a string of modhex digits.

    >>> hex_to_modhex('69b6481c8baba2b60e8f22179b58cd56')
    'hknhfjbrjnlnldnhcujvddbikngjrtgh'
    """
    return ''.join(map(hex_to_modhex_char, hex_str.lower()))

def modhex_to_hex(modhex_str):
    """
    Convert a string of modhex digits to a string of hex digits.

    >>> modhex_to_hex('hknhfjbrjnlnldnhcujvddbikngjrtgh')
    '69b6481c8baba2b60e8f22179b58cd56'
    """
    return ''.join(map(modhex_to_hex_char, modhex_str.lower()))


#
# Internals
#

def lookup(alist, key):
    return next(v for k, v in alist if k == key)

hex_chars    = '0123456789abcdef'
modhex_chars = 'cbdefghijklnrtuv'

hex_to_modhex_map = zip(hex_chars, modhex_chars)
modhex_to_hex_map = zip(modhex_chars, hex_chars)

hex_to_modhex_char = partial(lookup, hex_to_modhex_map)
modhex_to_hex_char = partial(lookup, modhex_to_hex_map)



if __name__ == "__main__":
    import doctest

    doctest.testmod()
