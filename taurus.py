#!/usr/bin/python

"""
Copyright (c) 2015 Finn Ellis, licensed under the MIT License.
(See accompanying LICENSE file for details.)
"""

import socket
import sys

import taunet
import filesystem


# Set up logger.
logger=filesystem.get_logger("taurus")


def send_message(tnu, message):
    tnm = taunet.TauNetMessage().outgoing(tnu.name, message)
    sender = socket.socket()
    sender.settimeout(3)
    sender.connect((tnu.host, tnu.port))
    sender.send(tnm.ciphertext)
    sender.shutdown(socket.SHUT_RDWR)
    sender.close()
    logger.info("Sent a message to {name} ({host}:{port}).".format(name=tnu.name, host=tnu.host, port=str(tnu.port)))
    filesystem.write_message(tnu.name, tnm)


if __name__ == "__main__":
    username = raw_input("Recipient username: ")
    tnu = taunet.users.by_name(username)
    if tnu == None:
        print("No such user. Known users: " + ", ".join(sorted([u.name for u in taunet.users.all()])))
        sys.exit(1)
    message = raw_input("Message: ")
    send_message(tnu, message)
