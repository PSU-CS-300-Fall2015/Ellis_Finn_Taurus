# Taurus

Copyright © 2015 Finn Ellis

A minimal client implementing the TauNet protocol developed by Bart Massey's PSU CS 300, Fall 2015. Taurus is licensed under the MIT License; see included file `LICENSE` for details.

## Usage

### Setup

Create directories for Taurus to work in:

```
mkdir -p ~/.taurus/messages
```

Create the file `~/.taurus/usertable.csv`, where each line is of the form `username,host,port`. Hosts can be either IPv4 addresses or hostnames. At least the username and host portions of the content (those parts which are required by the TauNet specification) should be identical to the information distributed to every other node on the TauNetwork. Port should normally be 6283 for everyone.

Update the variable `KEY` in `taunet.py` to the encryption key for the TauNetwork, and `USERNAME` to your username in the user table.

### Receiving Messages

Start the daemon with `./taurusd.py &`. It will listen for messages and check for all of the following:

* The message can be decrypted with the key in `taunet.py`.
* The headers and formatting of the cleartext conform to the TauNet specification.
* The message is of nonzero length.
* The message is addressed to the username specified in `taunet.py`.
* The message came from a username in the user table, with the correct IP or hostname.

If any of those is not true, the message is discarded and the reason is logged. If all of them are true, the message is timestamped and appended to a file in `~/.taurus/messages/` named after the sender.

### Sending Messages

Run `./taurus.py`. It will prompt for a username and verify that that name is in the user table. If it isn't, the list of available recipients will be displayed instead.

If the user is found, Taurus will prompt for a message and attempt to send it to the matching host. If it can't reach that host, it will display an error message.

Messages longer than the maximum guaranteed-possible length given by the TauNet protocol will be truncated to that length. (The guaranteed-possible length is the maximum overall message size minus the maximum header size.)

## Tests

`./encryption.py --test` to run internal consistency tests on the encryption functions.

`cd cs2-tests; ./test.sh` to verify their output against known data.

`test_messages/` contains text files which can be used to test various parts of the system. Specifically:

* `tnm.txt` is a TauNet v0.2-compliant message, including headers, with made-up usernames. It can be used to test the listener alone with something like:

```
cat test_messages/tnm.txt | ./ciphersaber2.py --key password | nc localhost 6283
```

* `long_lorem.txt` contains two lines, a username and a message, and is intended to be catted into `taurus.py`. The message is 1024 bytes long, and should automatically be truncated when sent.

## Logs

Both the sender and receiver log information in `~/.taurus/taurus.log`.
