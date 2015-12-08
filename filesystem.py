#!/usr/bin/python

"""
Copyright (c) 2015 Finn Ellis, licensed under the MIT License.
(See accompanying LICENSE file for details.)

The parts of Taurus which interact with the filesystem and are shared between
the sender and listener: logging and conversation records.
"""

import os
import fcntl
import time
import logging


# Ensure base directory exists.
TAURUS_DIR = os.path.expanduser("~/.taurus")
assert os.path.isdir(TAURUS_DIR), "Taurus directory {0} does not exist.".format(TAURUS_DIR)

# Ensure message directory exists.
MESSAGE_DIR = os.path.join(TAURUS_DIR, "messages")
assert os.path.isdir(MESSAGE_DIR), "Message directory {0} does not exist.".format(MESSAGE_DIR)

# Set up the common logger configuration.
LOG_FILE = os.path.join(TAURUS_DIR, "taurus.log")
LOG_FORMAT = "%(asctime)s %(levelname)s (%(name)s): %(message)s"
LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILE, format=LOG_FORMAT)


def get_logger(name):
    """
    Utility function to retrieve logger objects for other modules.
    """
    return logging.getLogger(name)

def write_message(conversation, tnm):
    """
    Write a TauNet message to the appropriate conversation in the message
    directory. tnm should be a valid TauNetMessage object, and conversation
    the name of the conversation file which should be updated (normally the
    name of the non-local user: the sender of incoming messages, and the
    recipient of outgoing ones).
    """
    filename = os.path.join(MESSAGE_DIR, conversation)
    line = "[{time}] {sender}: {message}\n".format(time=time.strftime("%c"), sender=tnm.sender, message=tnm.message)
    with open(filename, "a") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(line)
        fcntl.flock(f, fcntl.LOCK_UN)
    return filename

def conversations():
    """
    Return a list of the filenames of all conversations available for viewing.
    """
    return sorted(os.listdir(MESSAGE_DIR))
