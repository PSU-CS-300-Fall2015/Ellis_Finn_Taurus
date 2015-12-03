#!/usr/bin/python

"""
Copyright (c) 2015 Finn Ellis, licensed under the MIT License.
(See accompanying LICENSE file for details.)

The parts of Taurus which interact with the filesystem: logging and
conversation records.
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


def write_message(tnm):
    """
    Write a TauNet message to the appropriate conversation in the message
    directory. tnm should be a valid TauNetMessage object.
    """
    filename = os.path.join(MESSAGE_DIR, tnm.sender)
    line = "[{time}] {sender}: {message}\n".format(time=time.strftime("%c"), sender=tnm.sender, message=tnm.message)
    with open(filename, "a") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(line)
        fcntl.flock(f, fcntl.LOCK_UN)
    return filename
