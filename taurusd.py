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

            if not data:
                # The error message is here instead of above because the
                # exception isn't always raised.
                logger.info("Connection from {sender} timed out.".format(sender=sender))
                continue

            try:
                tnm = taunet.TauNetMessage().incoming(data)
            except taunet.TauNetError as e:
                logger.warning("Got a badly-formed message ('{error}'). Discarding.".format(error=str(e)))
                continue
            if not tnm.message:
                logger.info("Discarding zero-length message.")
                continue
            if tnm.recipient != taunet.USERNAME:
                logger.warning("Got a message for a user who's not us ({user}), discarding.".format(user=tnm.recipient))
                continue
            tnu = taunet.users.by_name(tnm.sender)
            if tnu == None:
                logger.warning("Got a message from an unknown user ({user}), discarding.".format(user=tnm.sender))
                continue
            correct_origin = socket.gethostbyname(tnu.host)
            if sender[0] != correct_origin:
                logger.warning("Got a message from a known user ({user}) at the wrong host ({wrong} instead of {right}), discarding.".format(user=tnm.sender, wrong=sender[0], right=correct_origin))
                continue
            if tnm.version != taunet.VERSION:
                # If it got this far, nothing seems to be wrong with it. Warn, but keep.
                logger.warning("Incoming message version doesn't match ours; may be malformed.")

            # Hooray! We got a nice message!
            filename = filesystem.write_message(tnm.sender, tnm)
            logger.info("Wrote message to {filename}.".format(filename=filename))

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
