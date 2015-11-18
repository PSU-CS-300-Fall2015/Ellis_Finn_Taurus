#!/usr/bin/python

"""
(c) 2015 Finn Ellis, licensed under MIT (see LICENSE).
Based on the pseudocode at https://github.com/BartMassey/ciphersaber2
"""

import random
import time


# Use OS-provided randomness instead of only software.
urandom = random.SystemRandom(time.clock())

# This is a default and can be overridden in function calls.
IV_LENGTH = 10


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


def random_iv(length = None):
    if length == None:
        length = IV_LENGTH
    iv = ""
    for i in range(length):
        iv += (chr(urandom.randrange(256)))
    return iv


def encrypt(message, rounds, key, iv = None):
    if iv == None:
        iv = random_iv()
    stream = keystream(len(message), rounds, key+iv)
    ciphertext = ""
    for i in range(len(message)):
        ciphertext += chr(ord(message[i]) ^ stream[i])
    return iv + ciphertext


def decrypt(ciphertext, rounds, key, iv_length = None):
    if iv_length == None:
        iv_length = IV_LENGTH
    iv = ciphertext[:iv_length]
    ciphertext = ciphertext[iv_length:]
    stream = keystream(len(ciphertext), rounds, key+iv)
    plaintext = ""
    for i in range(len(ciphertext)):
        plaintext += chr(ord(ciphertext[i]) ^ stream[i])
    return plaintext


if __name__ == "__main__":
    print("-- Testing stream generation. --")
    print("Generating a 10-byte stream, 200 rounds, key 'testkey'")
    stream = keystream(10, 200, "testkey")
    assert stream == keystream(10, 200, "testkey")
    print("Same input, same output.")
    assert stream != keystream(10, 200, "different key")
    print("Different input, different output.")
    assert len(keystream(42, 200, "testkey")) == 42
    print("Requested 42 bytes of stream, got 42 bytes of stream.")

    print("-- Testing encryption. --")
    print("Encrypting 'fish', 200 rounds, key 'testkey', IV 'badiv'")
    cipher = encrypt("fish", 200, "testkey", "badiv")
    assert cipher == encrypt("fish", 200, "testkey", "badiv")
    print("Same input, same output.")
    assert cipher != encrypt("fish", 200, "testkey")
    print("Random IV, different output.")
    iv = random_iv()
    random_cipher = encrypt("fish", 200, "testkey", iv)
    assert random_cipher.startswith(iv)
    print("Ciphertext starts with randomly-chosen IV.")

    print("-- Testing decryption. --")
    assert "fish" == decrypt(cipher, 200, "testkey", 5)
    print("Got 'fish' back from stream with selected IV.")
    assert "fish" == decrypt(random_cipher, 200, "testkey")
    print("Got 'fish' back from stream with random IV.")
    assert "fish" != decrypt(random_cipher, 200, "badkey")
    print("Didn't get 'fish' back when using the wrong key.")
