#!/usr/bin/python

"""
(c) 2015 Finn Ellis, licensed under MIT (see LICENSE).
Based on the pseudocode at https://github.com/BartMassey/ciphersaber2
"""

import random
import time

urandom = random.SystemRandom(time.clock())


def keystream(stream_length, rounds, key):
    S = range(256)

    # Do key scheduling.
    j = 0
    while rounds:
        for i in range(256):
            j = (j + S[i] + ord(key[i % len(key)])) % 256
            x = S[i]
            S[i] = S[j]
            S[j] = x
        rounds -= 1

    # Produce the actual stream.
    stream = []
    for i in range(stream_length):
        k = (i + 1) % 256
        j = (j + S[k]) % 256
        x = S[k]
        S[k] = S[j]
        S[j] = x
        stream.append(S[(S[k] + S[j]) % 256])

    return stream


def random_iv(length = 10):
    iv = ""
    for i in range(length):
        iv += (chr(urandom.randrange(256)))
    return iv


def encrypt(message, rounds, key, iv = None):
    if iv == None:
        iv = random_iv()
    stream = keystream(len(message), rounds, key+iv)
    ciphertext = iv
    for i in range(len(message)):
        ciphertext += (chr(ord(message[i]) ^ stream[i]))
    return ciphertext


if __name__ == "__main__":
    print("Testing stream generation.")
    print("Generating a 10-byte stream, 200 rounds, key 'testkey'")
    stream = keystream(10, 200, "testkey")
    print(stream)
    assert stream == keystream(10, 200, "testkey")
    print("Same input, same output.")
    assert stream != keystream(10, 200, "different key")
    print("Different input, different output.")
    assert len(keystream(42, 200, "testkey")) == 42
    print("Requested 42 bytes of stream, got 42 bytes of stream.")

    print("Testing encryption.")
    print("Encrypting 'fish', 200 rounds, key 'testkey', IV 'badiv'")
    cipher = encrypt("fish", 200, "testkey", "badiv")
    assert cipher == encrypt("fish", 200, "testkey", "badiv")
    print("Same input, same output.")
    assert cipher != encrypt("fish", 200, "testkey")
    print("Random IV, different output.")
    iv = random_iv()
    assert encrypt("fish", 200, "testkey", iv).startswith(iv)
    print("Ciphertext starts with IV.")
