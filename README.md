# Taurus

Copyright © 2015 Finn Ellis

A minimal client implementing the TauNet protocol developed by Bart Massey's PSU CS 300, Fall 2015. Taurus is licensed under the MIT License; see included file `LICENSE` for details.

## Usage

### Setup

Create directories for Taurus to work in:

```
mkdir -p ~/.taurus/messages
```

### Receiving Messages

Start the daemon with `./taurusd.py`. It will decrypt any received messages and write them into files in `~/.taurus/messages`, named after their senders and timestamps. Information is logged to `~/.taurus/taurusd.log`.

### Sending Messages

Not yet implemented. In the meantime, this does the trick, assuming `tnm` is a text file containing a properly-formatted TauNet message, and the variables contain what they say they do.

```
cat tnm | ./ciphersaber2.py --key $ENCRYPTION_KEY | nc $DESTINATION_IP 6283
```

## Tests

`./encryption.py --test` to run internal consistency tests on the encryption functions.

`cd cs2-tests; ./test.sh` to verify their output against known data.

`test_message` contains a TauNet v0.2-compliant message, including headers, in cleartext, which can be used with the above to test the daemon.
