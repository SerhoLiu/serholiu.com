#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hmac
import base64
import hashlib


rand_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def get_random_string(length=12):
    """
    Returns a random string of length characters from the set of a-z, A-Z, 0-9
    for use as a salt.

    The default length of 12 with the a-z, A-Z, 0-9 character set returns
    a 71-bit salt. log_2((26+26+10)^12) =~ 71 bits
    """
    import random

    try:
        random = random.SystemRandom()
    except NotImplementedError:
        pass
    return "".join([random.choice(rand_chars) for _ in range(length)])


class PasswordCrypto(object):

    ALGORITHM = "pbkdf2_sha256"
    ITERATIONS = 5000
    DIGEST = "sha256"

    @classmethod
    def get_encrypted(cls, password, salt=None, iterations=None):
        if not password:
            return None
        if (not salt) or ("$" in salt):
            salt = get_random_string()
        if not iterations:
            iterations = cls.ITERATIONS

        encrypted = hashlib.pbkdf2_hmac(
            cls.DIGEST,
            password.encode(),
            salt.encode(),
            iterations
        )

        return "{0}${1}${2}${3}".format(
            cls.ALGORITHM,
            cls.ITERATIONS,
            salt,
            base64.b64encode(encrypted).decode()
        )

    @classmethod
    def authenticate(cls, password, encrypted):
        algorithm, iterations, salt, _ = encrypted.split("$", 3)
        if algorithm != cls.ALGORITHM:
            return False
        encrypted_new = cls.get_encrypted(password, salt, int(iterations))

        return hmac.compare_digest(encrypted, encrypted_new)
