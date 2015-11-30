#!/usr/bin/python

"""
Copyright (c) 2015 Finn Ellis, licensed under the MIT License.
(See accompanying LICENSE file for details.)

This is a listening daemon for the TauNet protocol. It waits to receive
connections and attempts to parse any data sent as a well-formatted
TauNet message. If successful, it writes the message into a file in the
TauNet messages directory. If unsuccessful, it logs the reason.
"""

import socket
import logging
import os
import time

import taunet


# Network connection settings.
MAX_QUEUE = 10

# Ensure base directory exists.
TAURUS_DIR = os.path.expanduser("~/.taurus")
assert os.path.isdir(TAURUS_DIR), "Taurus directory {0} does not exist.".format(TAURUS_DIR)

# Ensure message directory exists.
MESSAGE_DIR = os.path.join(TAURUS_DIR, "messages")
assert os.path.isdir(MESSAGE_DIR), "Message directory {0} does not exist.".format(MESSAGE_DIR)

# Set up logger.
LOG_FILE = os.path.join(TAURUS_DIR, "taurusd.log")
LOG_FORMAT = "%(asctime)s %(levelname)s: %(message)s"
LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILE, format=LOG_FORMAT)
logger=logging.getLogger("taurusd")


def write_message(tnm):
    """
    Write a TauNet message to a file in the message directory.
    tnm should be a valid TauNetMessage object.
    """
    filename = tnm.sender + "-" + str(time.time())
    filename = os.path.join(MESSAGE_DIR, filename)
    with open(filename, "w") as f:
        f.write(tnm.cleartext)
    return filename


def main_loop():
    try:
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        assert listener, "Couldn't create listening socket."
        # Block until someone connects to us.
        listener.settimeout(None)
        # Empty host means "all available interfaces."
        listener.bind(('', taunet.PORT))
        listener.listen(MAX_QUEUE)

        while True:
            conn = None
            conn, sender = listener.accept()
            assert conn, "Failed to make connection socket"
            assert sender, "Made connection, but have no sender"
            logger.info("Got a connection from {sender}.".format(sender=sender))
            # Don't block when connected; time out if we get no data.
            conn.settimeout(3)
            data = conn.recv(taunet.BUF_SIZE)
            if data:
                try:
                    tnm = taunet.TauNetMessage(data)
                    filename = write_message(tnm)
                    logger.info("Wrote message to {filename}.".format(filename=filename))
                except taunet.TauNetError as e:
                    logger.info("Got a badly-formed message ('{error}').".format(error=str(e)))
            else:
                logger.info("Connection from {sender} timed out.".format(sender=sender))
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()

    # Will catch socket.error later; right now we want it to blow us up.
    except KeyboardInterrupt:
        logger.info("Killed.")
    finally:
        if conn:
            logger.info("Closing open socket.")
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()


if __name__ == "__main__":
    main_loop()