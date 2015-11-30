#!/usr/bin/python

import ciphersaber2


KEY = "password"
VERSION = "0.2"


class TauNetError(Exception):
    pass


class TauNetMessage(object):
    """
    TauNet message data. To parse an incoming message, pass in the ciphertext.
    """
    def __init__(self, ciphertext=None):
        self.ciphertext = ciphertext
        self.cleartext = ciphersaber2.decrypt(ciphertext, KEY)
        self.version = None
        # The header is called "from" but that's a python keyword.
        self.sender = None
        self.recipient = None
        self.message = None
        self.parse_headers()

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
