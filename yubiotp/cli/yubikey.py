"""
This is a command-line interface to the yubiotp package. Its primary function
is to simulate a YubiKey device for testing purposes. It also includes some
utilities for things like converting to and from modhex.
"""

from binascii import hexlify, unhexlify
import configparser
from optparse import Option, OptionGroup, OptionParser, OptionValueError
from os.path import expanduser
from random import choice
import sys

from yubiotp.modhex import hex_to_modhex, modhex, modhex_to_hex, unmodhex
from yubiotp.otp import YubiKey, decode_otp, encode_otp


def main():
    parser = Handler.global_option_parser()
    parser.disable_interspersed_args()

    opts, args = parser.parse_args()

    if len(args) == 0:
        usage('You must choose an action', parser)

    handlers = {
        'list': ListHandler(),
        'init': InitHandler(),
        'delete': DeleteHandler(),
        'gen': GenHandler(),
        'parse': ParseHandler(),
        'modhex': ModhexHandler(),
    }

    handler = handlers.get(args[0])

    if handler is None:
        usage('Unknown action: {0}'.format(args[0]), parser)
    else:
        handler.run()


def check_hex_value(option, opt, value):
    try:
        unhexlify(value.encode())
    except TypeError as e:
        raise OptionValueError(str(e))

    return value


def check_modhex_value(option, opt, value):
    try:
        unmodhex(value.encode())
    except ValueError as e:
        raise OptionValueError(str(e))

    return value


class YubiKeyOption(Option):
    """
    Custom optparse Option class that adds the 'hex' value type. Values of this
    type are expected to be strings of hex digits, which will be decoded into
    binary strings before being stored.
    """

    TYPES = Option.TYPES + ('hex', 'modhex')
    TYPE_CHECKER = dict(
        Option.TYPE_CHECKER, hex=check_hex_value, modhex=check_modhex_value
    )


make_option = YubiKeyOption


class Handler(object):
    name = ''
    options = [
        make_option(
            '-f',
            '--config',
            dest='config',
            default='~/.yubikey',
            metavar='PATH',
            help='A config file to store device state. [%default]',
        ),
        make_option(
            '-n',
            '--name',
            dest='device_name',
            default='0',
            metavar='NAME',
            help='The device number or name to operate on. [%default]',
        ),
    ]
    args = ''
    description = 'Simulates one or more YubiKey devices from which you can generate tokens. Also parses tokens for verification. Choose an action for more information.'

    def run(self):
        parser = self.make_option_parser()

        opts, args = parser.parse_args()

        self.handle(opts, args)

    def make_option_parser(self):
        usage = '%prog [global opts] {0} [any opts]'.format(self.name)
        if self.args:
            usage = usage + ' ' + self.args

        parser = OptionParser(usage=usage, description=self.description)

        for option in Handler.options:
            parser.add_option(option)

        if len(self.options) > 0:
            group = OptionGroup(parser, self.name)
            for option in self.options:
                group.add_option(option)

            parser.add_option_group(group)

        return parser

    def handle(self, opts, args):
        raise NotImplementedError()

    @classmethod
    def global_option_parser(cls):
        parser = OptionParser(
            usage='%prog [global opts] <list|init|delete|gen|parse|modhex> [any opts] [args]',
            description=cls.description,
        )

        for option in cls.options:
            parser.add_option(option)

        return parser

    @staticmethod
    def random_hex(count):
        return ''.join(choice('0123456789abcdef') for i in range(count * 2))


class ListHandler(Handler):
    name = 'list'
    options = []
    args = ''
    description = 'List all virtual YubiKey devices.'

    def handle(self, opts, args):
        config = configparser.ConfigParser()
        config.read([expanduser(opts.config)])
        config.write(sys.stdout)


class InitHandler(Handler):
    name = 'init'
    options = [
        make_option(
            '-p',
            '--public',
            dest='public_id',
            type='modhex',
            default='',
            help='A modhex-encoded public ID (up to 16 bytes)',
        ),
        make_option(
            '-k',
            '--key',
            dest='key',
            type='hex',
            help='A hex-encoded 16-byte AES key. If omitted, one will be generated.',
        ),
        make_option(
            '-u',
            '--uid',
            dest='uid',
            type='hex',
            help='A hex-encoded 6-byte private ID. If omitted, one will be generated.',
        ),
        make_option(
            '-s',
            '--session',
            dest='session',
            type='int',
            default=0,
            help='The initial session counter. [%default]',
        ),
    ]
    description = 'Initialize a new virtual YubiKey.'

    def handle(self, opts, args):
        if opts.key is None:
            opts.key = self.random_hex(16)

        if opts.uid is None:
            opts.uid = self.random_hex(6)

        device = Device(opts.config, opts.device_name)
        device.create(opts.public_id, opts.key, opts.uid, opts.session)
        device.save()


class DeleteHandler(Handler):
    name = 'delete'
    options = []
    args = ''
    description = 'Remove a virtual YubiKey device.'

    def handle(self, opts, args):
        device = Device(opts.config, opts.device_name)
        device.delete()
        device.save()


class GenHandler(Handler):
    name = 'gen'
    options = [
        make_option(
            '-c',
            '--count',
            dest='count',
            type='int',
            default=1,
            help='Generate multiple tokens. [%default]',
        ),
        make_option(
            '-i',
            '--interactive',
            action='store_true',
            dest='interactive',
            help='Generate a token for every line read from stdin until interrupted.',
        ),
    ]
    args = ''
    description = 'Generate one or more tokens from the virtual device. This simulates pressing the YubiKey\'s button.'

    def handle(self, opts, args):
        device = Device(opts.config, opts.device_name)

        for i in range(opts.count):
            print(device.gen_token().decode())

        if opts.interactive:
            try:
                while True:
                    sys.stdin.readline()
                    print(device.gen_token().decode())
            except KeyboardInterrupt:
                pass

        device.save()


class ParseHandler(Handler):
    name = 'parse'
    options = []
    args = 'token ...'
    description = (
        'Parse tokens generated by the selected virtual device and display its fields.'
    )

    def handle(self, opts, args):
        device = Device(opts.config, opts.device_name)
        key = device.get_config('key', unhex=True)

        for token in args[1:]:
            try:
                public_id, otp = decode_otp(token.encode(), key)
            except ValueError as e:
                print(e)
            else:
                print('public_id: {0}'.format(public_id.decode()))
                print('uid: {0}'.format(hexlify(otp.uid).decode()))
                print('session: {0}'.format(otp.session))
                print('timestamp: 0x{0:x}'.format(otp.timestamp))
                print('counter: {0}'.format(otp.counter))
                print('random: 0x{0:x}'.format(otp.rand))
                print()


class ModhexHandler(Handler):
    name = 'modhex'
    options = [
        make_option(
            '-d',
            '--decode',
            action='store_true',
            dest='decode',
            help='Decode from modhex. Default is to encode to modhex.',
        ),
        make_option(
            '-H',
            '--hex',
            action='store_true',
            dest='hex',
            help='Encode to or decode from a string of hex digits. Default is a raw string.',
        ),
    ]
    args = 'input ...'
    description = 'Encode (default) or decode a modhex string.'

    def handle(self, opts, args):
        for arg in args[1:]:
            try:
                if opts.decode:
                    if opts.hex:
                        print(modhex_to_hex(arg.encode()).decode())
                    else:
                        print(unmodhex(arg.encode()).decode())
                else:
                    if opts.hex:
                        print(hex_to_modhex(arg.encode()).decode())
                    else:
                        print(modhex(arg.encode()).decode())
            except ValueError as e:
                print(e, file=sys.stderr)


def usage(message, parser=None):
    print(message)
    print()

    if parser is not None:
        parser.print_help()

    sys.exit(1)


class Device(object):
    def __init__(self, config_path, name):
        self.config_path = expanduser(config_path)
        self.name = name
        self.section_name = 'device_{0}'.format(name)

        self.config = self._load_config()
        self.yubikey = None

    def _load_config(self):
        config = configparser.ConfigParser()
        config.read([self.config_path])

        return config

    def create(self, public_id, key, uid, session):
        if len(key) != 32:
            raise ValueError('AES keys must be exactly 16 bytes')

        try:
            self.config.add_section(self.section_name)
        except configparser.DuplicateSectionError:
            usage('A device named "{0}" already exists.'.format(self.name))
        else:
            self.set_config('public_id', public_id)
            self.set_config('key', key)
            self.set_config('uid', uid)
            self.set_config('session', session)

    def delete(self):
        try:
            self.config.remove_section(self.section_name)
        except configparser.NoSectionError:
            usage('The device named "{0}" does not exist.'.format(self.name))

    def gen_token(self):
        self.ensure_yubikey()

        otp = self.yubikey.generate()
        key = self.get_config('key', unhex=True)
        public_id = self.get_config('public_id').encode()

        token = encode_otp(otp, key, public_id=public_id)

        return token

    def ensure_yubikey(self):
        if self.yubikey is None:
            try:
                uid = self.get_config('uid', unhex=True)
                session = int(self.get_config('session'))

                self.get_config('key')
            except Exception as e:
                usage(
                    'The device named "{0}" does not exist or is corrupt. ({1})'.format(
                        self.name, e
                    )
                )
            else:
                self.yubikey = YubiKey(uid=uid, session=session)

        return self.yubikey

    def save(self):
        if self.yubikey is not None:
            self.set_config('session', self.yubikey.session + 1)

        with open(self.config_path, 'w') as f:
            self.config.write(f)

    def get_config(self, key, unhex=False):
        value = self.config.get(self.section_name, key)
        if unhex:
            value = unhexlify(value.encode())

        return value

    def set_config(self, key, value):
        self.config.set(self.section_name, key, str(value))


if __name__ == '__main__':
    main()
