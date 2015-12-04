#!/bin/bash

# Copyright (c) 2015 Finn Ellis, licensed under the MIT license.
# (See accompanying LICENSE file for details.)

# Continuously checks whether the TauNet port appears in netstat's
# default output (i.e. is bound) and doesn't exit until it's not.
# Suggested usage: ./await_port.sh; ./taurusd.py &

echo -n 'Waiting for port ...'
while netstat | grep -q 6283; do
    echo -n '.'
    sleep 1
done
echo ' ready.'
