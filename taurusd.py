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

import taunet
import filesystem


# Network connection settings.
MAX_QUEUE = 10

# Get our logger object.
logger=filesystem.get_logger("taurusd")


def main_loop():
    logger.info("Starting main loop.")
    conn = None
    try:
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        assert listener, "Couldn't create listening socket."
        # Block until someone connects to us.
        listener.settimeout(None)
        # Empty host means "all available interfaces."
        listener.bind(('', taunet.PORT))
        listener.listen(MAX_QUEUE)

        while True:
            # Not redundant. The first initialization of conn is so that it can
            # be tested in the finally block even if an exception is raised
            # before now, this one is so it happens in every loop iteration.
            conn = None
            conn, sender = listener.accept()
            assert conn, "Failed to make connection socket"
            assert sender, "Made connection, but have no sender"
            logger.info("Got a connection from {sender}.".format(sender=sender))
            # Don't block when connected; time out if we get no data.
            conn.settimeout(3)
            try:
                data = conn.recv(taunet.BUF_SIZE)
            except socket.timeout:
                data = None
            if data:
                try:
                    tnm = taunet.TauNetMessage().incoming(data)
                    filename = filesystem.write_message(tnm)
                    logger.info("Wrote message to {filename}.".format(filename=filename))
                except taunet.TauNetError as e:
                    logger.info("Got a badly-formed message ('{error}').".format(error=str(e)))
            else:
                # The error message is here instead of above because the
                # exception isn't always raised.
                logger.info("Connection from {sender} timed out.".format(sender=sender))

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
