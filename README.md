# Taurus

Copyright © 2015 Finn Ellis

A minimal client implementing the TauNet protocol developed by Bart Massey's PSU CS 300, Fall 2015. Taurus is licensed under the MIT License; see included file `LICENSE` for details.

## Usage

Taurus, like other TauNet clients, is designed to be run under Raspbian Linux on a Raspberry Pi 2 Model B. This is the only supported environment, and it is strongly recommended. A single-user machine is ideal, both because the listening daemon isn't able to support multiple users, and because information stored on the local filesystem is not encrypted.

### Setup

Create directories for Taurus to work in:

```
mkdir -p ~/.taurus/messages
```

Create the file `~/.taurus/usertable.csv`, where each line is of the form `username,host,port`. Hosts can be either IPv4 addresses or hostnames. At least the username and host portions of the content (those parts which are required by the TauNet specification) should be identical to the information distributed to every other node on the TauNetwork. Port should normally be 6283 for everyone.

Update the variable `KEY` in `taunet.py` to the encryption key for the TauNetwork, and `USERNAME` to your username in the user table.

### The Listening Daemon

Start the daemon with `./taurusd.py &`. It will listen for messages and check for all of the following:

* The transmission is of nonzero length.
* The message can be decrypted with the key in `taunet.py`.
* The headers and formatting of the cleartext conform to the TauNet specification.
* The message is addressed to the username specified in `taunet.py`.
* The message came from a username in the user table, with the correct IP or hostname.

If any of those is not true, the message is discarded and the reason is logged (except the empty transmission, which is treated as a test connection). If all of them are true, the message is timestamped and appended to a file in `~/.taurus/messages/` named after the sender.

### The Client

Run `./taurus.py` to start the Taunet client. The main menu options are as follows:

#### Read Messages

This will present you with a list of existing conversations. You can select one by typing enough of the name for your choice to be unique. (To intput a username which is an initial substring of another username, hit enter when you're finished typing it.) This will show you up to 20 lines of conversation backlog, and will update as new messages come in.

#### Send a Message

Type a username. Taunet will check if the user is online and able to receive messages, and if so, will prompt you for a message to send and then send it. Messages longer than the maximum guaranteed-possible length given by the TauNet protocol will be truncated to that length. (The guaranteed-possible length is the maximum overall message size minus the maximum header size.)

#### Update Node Status

Taunet stores the last known online status (available or unavailable) for each node in the network. Use this command to update that information by attempting to send an empty test message to each node. This may take a few minutes, depending on your network size! (It will display its progress as it goes.)

#### View User List

This simply lists the other users to whom you can send messages. Any that were online last time Taunet checked will be marked with an asterisk. You can refresh this information by updating the node status (see above).

## Tests

`./encryption.py --test` to run internal consistency tests on the encryption functions.

`cd cs2-tests; ./test.sh` to verify their output against known data.

`test_messages/` contains text files which can be used to test various parts of the system. Specifically:

* `tnm.txt` is a TauNet v0.2-compliant message, including headers, with made-up usernames. It can be used to test the listener alone with something like:

```
cat test_messages/tnm.txt | ./ciphersaber2.py --key password | nc localhost 6283
```

* `long_lorem.txt` contains 1025 bytes of lorem ipsum, including a trailing newline, for easy pasting into messages. (This is too long to be contained in a TauNet 0.2-compliant messages, and should be truncated by the client.)

## Logs

Both the sender and receiver log information in `~/.taurus/taurus.log`.
