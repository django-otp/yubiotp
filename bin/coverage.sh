#!/bin/sh

config="yubikey-test.conf"

function yubikey ()
{
    coverage run -a --source=yubiotp,. -- ./yubikey -f $config "$@"
}


if [ -e $config ]; then
    unlink $config
fi

if [ -e .coverage ]; then
    unlink .coverage
fi

yubikey init -k 00112233445566778899aabbccddeeff -u 0123456789abcd -s 3 -p cccccccb
yubikey -n 1 init
yubikey list
yubikey -n 1 delete
yubikey gen
tmp=$(yubikey gen)
yubikey parse ${tmp}

tmp=$(yubikey modhex 'abcxyz')
yubikey modhex -d ${tmp}
tmp=$(yubikey modhex -H '61626378797a')
yubikey modhex -H -d ${tmp}
yubikey modhex -d ${tmp}

yubikey modhex

# Errors
yubikey -n 1 gen
yubikey -n 1 delete
yubikey -n 0 init
yubikey -n 1 init -k 0123
yubikey bogus
yubikey modhex -d xyz
yubikey parse bogus
yubikey init -k xyz
yubikey init -p xyz
yubikey


if [ -e $config ]; then
    unlink $config
fi
