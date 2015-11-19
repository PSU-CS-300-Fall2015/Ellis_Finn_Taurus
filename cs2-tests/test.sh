#!/bin/bash

# Copyright © 2015 Finn Ellis

# Tests CipherSaber2 implementation in the parent directory
# against some known samples. Cribbed heavily from Bart Massey's CS2 tests:
# https://github.com/BartMassey/ciphersaber2

TESTFILE=`mktemp`

cat <<EOF |
cstest1.cs1 asdfg cstest1.txt 1
cstest2.cs1 SecretMessageforCongress cstest2.txt 1
cknight.cs1 ThomasJefferson cknight.gif 1
cstest.cs2 asdfg cstest.txt 10
EOF
while read CIPHER KEY PLAIN R
do
    echo -n "Testing $CIPHER ... "
    cat $CIPHER | ../encryption.py -dk $KEY -r $R > $TESTFILE
    cmp --quiet $TESTFILE $PLAIN && echo "OK" || echo "!!"
done
rm $TESTFILE
