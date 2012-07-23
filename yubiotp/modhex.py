"""
Implementation of `modhex encoding <http://www.yubico.com/modhex-calculator>`_,
which uses keyboard-independent characters.

::

    hex digit:    0123456789abcdef
    modhex digit: cbdefghijklnrtuv
"""

from binascii import hexlify, unhexlify
from functools import partial

__all__ = ['modhex', 'unmodhex', 'is_modhex', 'hex_to_modhex', 'modhex_to_hex']


def modhex(data):
    """
    Encode a string of bytes as modhex.

    >>> modhex('abcdefghijklmnop')
    'hbhdhehfhghhhihjhkhlhnhrhthuhvic'
    """
    return hex_to_modhex(hexlify(data))

def unmodhex(encoded):
    """
    Decode a modhex string to its binary form.

    >>> unmodhex('hbhdhehfhghhhihjhkhlhnhrhthuhvic')
    'abcdefghijklmnop'
    """
    return unhexlify(modhex_to_hex(encoded))

def is_modhex(encoded):
    """
    Returns ``True`` iff the given string is valid modhex.

    >>> is_modhex('cbdefghijklnrtuv')
    True
    >>> is_modhex('cbdefghijklnrtuvv')
    False
    >>> is_modhex('cbdefghijklnrtuvyy')
    False
    """
    if any(c not in modhex_chars for c in encoded):
        return False
    elif len(encoded) % 2 != 0:
        return False
    else:
        return True

def hex_to_modhex(hex_str):
    """
    Convert a string of hex digits to a string of modhex digits.

    >>> hex_to_modhex('69b6481c8baba2b60e8f22179b58cd56')
    'hknhfjbrjnlnldnhcujvddbikngjrtgh'
    >>> hex_to_modhex('6j')
    Traceback (most recent call last):
        ...
    ValueError: Illegal hex character in input
    """
    try:
        return ''.join(map(hex_to_modhex_char, hex_str.lower()))
    except StopIteration:
        raise ValueError('Illegal hex character in input')

def modhex_to_hex(modhex_str):
    """
    Convert a string of modhex digits to a string of hex digits.

    >>> modhex_to_hex('hknhfjbrjnlnldnhcujvddbikngjrtgh')
    '69b6481c8baba2b60e8f22179b58cd56'
    >>> modhex_to_hex('hbhdxx')
    Traceback (most recent call last):
        ...
    ValueError: Illegal modhex character in input
    """
    try:
        return ''.join(map(modhex_to_hex_char, modhex_str.lower()))
    except StopIteration:
        raise ValueError('Illegal modhex character in input')


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
