#!/usr/bin/python

import socket
import logging

TAUNET_PORT = 6283
MAX_QUEUE = 10
BUF_SIZE = 1024

logging.basicConfig(level=logging.DEBUG)

# Initialize socket variables so we can test for their existence
# and close them cleanly in the finally block.
listener = None
conn = None
try:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    assert listener, "Couldn't create listening socket."
    # Block until we get data.
    listener.settimeout(None)
    # Empty host means "all available interfaces."
    listener.bind(('', TAUNET_PORT))
    listener.listen(MAX_QUEUE)

    conn, sender = listener.accept()
    assert conn, "Couldn't make connection socket"
    assert sender, "Made connection, but have no sender o_O"
    logging.info("Got a connection from {sender}.".format(sender=sender))
    # Don't block; time out after three seconds.
    conn.settimeout(3)
    data = conn.recv(BUF_SIZE)
    if data:
        logging.info("{sender} wrote: {data}".format(sender=sender, data=data))
    else:
        logging.info("Connection from {sender} timed out.".format(sender=sender))

# Will catch socket.error later; right now we want it to blow us up.
except KeyboardInterrupt:
    logging.info("Killed.")
finally:
    logging.info("Closing socket.")
    if listener:
        # No shutdown because this is just the listener, not a connection.
        listener.close()
    if conn:
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
