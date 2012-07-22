#!/bin/sh

config="~/.yubikey-test"

function yubikey ()
{
    ./yubikey -f $config "$@"
}


unlink $config 2>/dev/null

yubikey init -k 00112233445566778899aabbccddeeff -u abcdef -s 3 -P username
yubikey -n 1 init
yubikey list

token=`yubikey gen`
echo $token
yubikey parse $token
yubikey -n 1 parse $token
yubikey delete
yubikey -n 1 delete

modhex=`yubikey modhex modhex-test`
echo $modhex
yubikey modhex -d $modhex

unlink $config 2>/dev/null