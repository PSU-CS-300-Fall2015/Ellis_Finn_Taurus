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
    user_string = "{user} ({host}:{port})".format(user=tnu.name, host=tnu.host, port=str(tnu.port))
    sender = socket.socket()
    sender.settimeout(3)
    try:
        sender.connect((tnu.host, tnu.port))
        sender.send(tnm.ciphertext)
    except socket.timeout as e:
        print("Unable to reach {user}: {reason}".format(user=user_string, reason=str(e)))
        logger.error("Failed to send a message to {user}: {reason}".format(user=user_string, reason=str(e)))
    else:
        logger.info("Sent a message to {user}.".format(user=user_string))
        filesystem.write_message(tnu.name, tnm)
    sender.shutdown(socket.SHUT_RDWR)
    sender.close()


if __name__ == "__main__":
    username = raw_input("Recipient username: ")
    tnu = taunet.users.by_name(username)
    if tnu == None:
        print("No such user. Known users: " + ", ".join(sorted([u.name for u in taunet.users.all()])))
        sys.exit(1)
    message = raw_input("Message: ")
    send_message(tnu, message)
