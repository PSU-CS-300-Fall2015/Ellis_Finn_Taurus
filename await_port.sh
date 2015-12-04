#!/bin/bash

echo -n 'Waiting for port ...'
while netstat | grep -q 6283; do
    echo -n '.'
    sleep 1
done
echo ' ready.'
