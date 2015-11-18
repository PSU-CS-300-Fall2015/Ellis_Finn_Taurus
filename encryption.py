#!/usr/bin/python

"""
Copyright (c) 2015 Finn Ellis, licensed under the MIT License.
(See accompanying LICENSE file for details.)

The functions in this file are based on Bart Massey's pseudocode:
https://github.com/BartMassey/ciphersaber2
"""

import random
import time


# Use OS-provided randomness instead of only software.
urandom = random.SystemRandom(time.clock())

# These are just defaults, based on the CipherSaber2 specification.
# They can be overridden in the actual function calls.
IV_LENGTH = 10
ROUNDS = 200


def keystream(stream_length, key, rounds = None):
    """
    Generate an RC4 keystream of the given length, doing a specified number
    of rounds of key scheduling and encrypting with the key provided.
    """
    if rounds == None:
        rounds = ROUNDS

    # Do key scheduling.
    j = 0
    S = range(256)
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
    """
    Randomly create an initial value of the length provided, or the default.
    """
    if length == None:
        length = IV_LENGTH
    iv = ""
    for i in range(length):
        iv += (chr(urandom.randrange(256)))
    return iv


def encrypt(message, key, rounds = None, iv = None):
    """
    Encrypt a message with the given key, doing the specified number of rounds
    of key scheduling. Creates a random IV if none was provided.
    """
    if rounds == None:
        rounds = ROUNDS
    if iv == None:
        iv = random_iv()
    stream = keystream(len(message), key+iv, rounds)
    ciphertext = ""
    for i in range(len(message)):
        ciphertext += chr(ord(message[i]) ^ stream[i])
    return iv + ciphertext


def decrypt(ciphertext, key, rounds = None, iv_length = None):
    """
    Decrypt a message with the given key, doing the specified number of rounds
    of key scheduling. If no IV length is provided, assumes the default.
    """
    if rounds == None:
        rounds = ROUNDS
    if iv_length == None:
        iv_length = IV_LENGTH
    iv = ciphertext[:iv_length]
    ciphertext = ciphertext[iv_length:]
    stream = keystream(len(ciphertext), key+iv, rounds)
    plaintext = ""
    for i in range(len(ciphertext)):
        plaintext += chr(ord(ciphertext[i]) ^ stream[i])
    return plaintext


def run_tests():
    """
    A few simple tests for the encryption functions.
    """

    print("-- Testing stream generation. --")
    print("Generating a 10-byte stream, 200 rounds, key 'testkey'")
    stream = keystream(10, "testkey", 200)
    assert stream == keystream(10, "testkey", 200)
    print("Same input, same output.")
    assert stream != keystream(10, "different key", 200)
    print("Different input, different output.")
    assert len(keystream(42, "testkey", 200)) == 42
    print("Requested 42 bytes of stream, got 42 bytes of stream.")

    print("-- Testing encryption. --")
    print("Encrypting 'fish', 200 rounds, key 'testkey', IV 'badiv'")
    cipher = encrypt("fish", "testkey", 200, "badiv")
    assert cipher == encrypt("fish", "testkey", 200, "badiv")
    print("Same input, same output.")
    assert cipher != encrypt("fish", "testkey", 200)
    print("Random IV, different output.")
    iv = random_iv()
    random_cipher = encrypt("fish", "testkey", 200, iv)
    assert random_cipher.startswith(iv)
    print("Ciphertext starts with randomly-chosen IV.")

    print("-- Testing decryption. --")
    assert "fish" == decrypt(cipher, "testkey", 200, 5)
    print("Got 'fish' back from stream with selected IV.")
    assert "fish" == decrypt(random_cipher, "testkey", 200)
    print("Got 'fish' back from stream with random IV.")
    assert "fish" != decrypt(random_cipher, "badkey", 200)
    print("Didn't get 'fish' back when using the wrong key.")

    print("-- Testing defaults. --")
    cipher = encrypt("fish", "testkey")
    assert "fish" == decrypt(cipher, "testkey")
    print("Encrypt/decrypt match.")
    assert "fish" == decrypt(cipher, "testkey", ROUNDS, IV_LENGTH)
    print("Constants match.")


if __name__ == "__main__":
    run_tests()
