#!/usr/bin/python

"""
Copyright (c) 2015 Finn Ellis, licensed under the MIT License.
(See accompanying LICENSE file for details.)

This file defines constants and classes related to the TauNet protocol.
Specifically, the TauNetMessage class manages encryption and headers
for incoming and outgoing messages.
"""

import ciphersaber2


VERSION = "0.2"
BUF_SIZE = 1024
PORT = 6283
KEY = "password"


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
