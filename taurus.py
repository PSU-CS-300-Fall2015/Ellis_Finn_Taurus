#!/usr/bin/python

"""
Copyright (c) 2015 Finn Ellis, licensed under the MIT License.
(See accompanying LICENSE file for details.)
"""

import socket

import taunet
import filesystem


# Set up logger.
logger=filesystem.get_logger("taurus")


def send_message(recipient, message):
    tnm = taunet.TauNetMessage().outgoing(recipient, message)
    sender = socket.socket()
    sender.settimeout(3)
    sender.connect(("127.0.0.1", 6283))
    sender.send(tnm.ciphertext)
    sender.shutdown(socket.SHUT_RDWR)
    sender.close()
    logger.info("Sent a message to myself.")
    filesystem.write_message(tnm)


if __name__ == "__main__":
    send_message("relsqui", "Two of this message.")
