#!/usr/bin/python

"""
Copyright (c) 2015 Finn Ellis, licensed under the MIT License.
(See accompanying LICENSE file for details.)

This file defines constants and classes related to the TauNet protocol.
Specifically, the TauNetMessage class manages encryption and headers
for incoming and outgoing messages.
"""

import os
import fcntl
import csv

import ciphersaber2
import filesystem


VERSION = "0.2"
BUF_SIZE = 1024
PORT = 6283
KEY = "password"
USERNAME = "relsqui"


class TauNetError(Exception):
    pass


class TauNetMessage(object):
    """
    TauNet message data. To parse an incoming message, pass in the ciphertext.
    """
    def __init__(self):
        self.ciphertext = None
        self.cleartext = None
        self.version = None
        # The header is called "from" but that's a python keyword.
        self.sender = None
        self.recipient = None
        self.message = None

    def incoming(self, ciphertext):
        self.ciphertext = ciphertext
        self.cleartext = ciphersaber2.decrypt(ciphertext, KEY)
        self.parse_headers()
        return self

    def outgoing(self, recipient, message):
        self.recipient = recipient
        self.sender = USERNAME
        self.message = message
        self.version = VERSION
        self.cleartext = self.build_headers() + message
        self.ciphertext = ciphersaber2.encrypt(self.cleartext, KEY)
        return self

    def build_headers(self):
        headers = []
        headers.append("version: " + self.version)
        headers.append("from: " + self.sender)
        headers.append("to: " + self.recipient)
        headers.append("\r\n")
        return "\r\n".join(headers)

    def parse_headers(self):
        cleartext = self.cleartext
        headers = {}
        try:
            headers["version"], cleartext = cleartext.split("\r\n", 1)
            headers["from"], cleartext = cleartext.split("\r\n", 1)
            headers["to"], cleartext = cleartext.split("\r\n", 1)
        except ValueError:
            raise TauNetError("Wrong header count or bad separators.")
        for header in headers:
            if not headers[header].startswith(header + ": "):
                raise TauNetError("Header format error: {0}".format(headers[header]))
            headers[header] = headers[header][len(header)+2:]
            if not headers[header]:
                raise TauNetError("Empty '{0}' header.".format(header))
        if not cleartext.startswith("\r\n"):
            raise TauNetError("No blank line after headers.")
        cleartext = cleartext[2:]
        self.message = cleartext
        self.version = headers["version"]
        self.sender = headers["from"]
        self.recipient = headers["to"]

    def version_ok(self):
        if self.version == VERSION:
            return True
        return False


class TauNetUser(object):
    """
    A single TauNet user from the network's user table.
    """
    def __init__(self, name, host, port=6283):
        self.name = name
        self.host = host
        self.port = port


class UserTable(object):
    def __init__(self):
        self.load_users()

    def load_users(self):
        """
        Parse the user table file and populate lists of TauNetUser objects.
        """
        self.users_by_host = {}
        self.users_by_name = {}
        self.all_users = []
        with open(os.path.join(filesystem.TAURUS_DIR, "users.csv"), "r") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            reader = csv.reader(f.readlines())
            fcntl.flock(f, fcntl.LOCK_UN)
        for user in reader:
            tnu = TauNetUser(user[0], user[1], int(user[2]))
            self.users_by_host[user[1]] = tnu
            self.users_by_name[user[0]] = tnu
            self.all_users.append(tnu)

    def all(self):
        """
        Fetch the complete user list. This is a function just for consistency
        with the other two user-fetching functions.
        """
        return self.all_users

    def by_name(self, name):
        """
        Check the user table for a TauNetUser with the name given. If found,
        return it. Otherwise, return None.
        """
        return self.users_by_name.get(name)

    def by_host(self, host):
        """
        Check the user table for a TauNetUser with the host given. If found,
        return it. Otherwise, return None.
        """
        return self.users_by_host.get(host)


users = UserTable()
