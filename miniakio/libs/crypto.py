"""
Django's standard crypto functions and utilities.
"""

import struct
import hashlib
import binascii
import operator


trans_5c = "".join([chr(x ^ 0x5C) for x in xrange(256)])
trans_36 = "".join([chr(x ^ 0x36) for x in xrange(256)])


def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
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
    return ''.join([random.choice(allowed_chars) for i in range(length)])


def constant_time_compare(val1, val2):
    """
    Returns True if the two strings are equal, False otherwise.

    The time taken is independent of the number of characters that match.
    """
    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in zip(val1, val2):
        result |= ord(x) ^ ord(y)
    return result == 0


def bin_to_long(x):
    """
    Convert a binary string into a long integer

    This is a clever optimization for fast xor vector math
    """
    return long(x.encode('hex'), 16)


def long_to_bin(x):
    """
    Convert a long integer into a binary string
    """
    hex = "%x" % (x)
    if len(hex) % 2 == 1:
        hex = '0' + hex
    return binascii.unhexlify(hex)


def fast_hmac(key, msg, digest):
    """
    A trimmed down version of Python's HMAC implementation
    """
    dig1, dig2 = digest(), digest()
    if len(key) > dig1.block_size:
        key = digest(key).digest()
    key += chr(0) * (dig1.block_size - len(key))
    dig1.update(key.translate(trans_36))
    dig1.update(msg)
    dig2.update(key.translate(trans_5c))
    dig2.update(dig1.digest())
    return dig2


def pbkdf2(password, salt, iterations, dklen=0, digest=None):
    """
    Implements PBKDF2 as defined in RFC 2898, section 5.2

    HMAC+SHA256 is used as the default pseudo random function.

    Right now 10,000 iterations is the recommended default which takes
    100ms on a 2.2Ghz Core 2 Duo.  This is probably the bare minimum
    for security given 1000 iterations was recommended in 2001. This
    code is very well optimized for CPython and is only four times
    slower than openssl's implementation.
    """
    assert iterations > 0
    if not digest:
        digest = hashlib.sha256
    hlen = digest().digest_size
    if not dklen:
        dklen = hlen
    if dklen > (2 ** 32 - 1) * hlen:
        raise OverflowError('dklen too big')
    l = -(-dklen // hlen)
    r = dklen - (l - 1) * hlen

    def F(i):
        def U():
            u = salt + struct.pack('>I', i)
            for j in xrange(int(iterations)):
                u = fast_hmac(password, u, digest).digest()
                yield bin_to_long(u)
        return long_to_bin(reduce(operator.xor, U()))

    T = [F(x) for x in range(1, l + 1)]
    return ''.join(T[:-1]) + T[-1][:r]


class PasswordCrypto(object):

    ALGORITHM = "pbkdf2_sha256"
    ITERATIONS = 5000
    DIGEST = hashlib.sha256

    @classmethod
    def get_encrypted(cls, password, salt=None, iterations=None):
        if not password:
            return None
        if (not salt) or ('$' in salt):
            salt = get_random_string()
        if not iterations:
            iterations = cls.ITERATIONS
        password = str(password)
        encrypted = pbkdf2(password, salt, iterations, digest=cls.DIGEST)
        encrypted = encrypted.encode('base64').strip()
        return "%s$%d$%s$%s" % (cls.ALGORITHM, cls.ITERATIONS, salt, encrypted)
    
    @classmethod
    def authenticate(cls, password, encrypted):
        algorithm, iterations, salt, encrypt = encrypted.split('$', 3)
        if algorithm != cls.ALGORITHM:
            return False
        encrypted_new = cls.get_encrypted(password, salt, int(iterations))
        return constant_time_compare(encrypted, encrypted_new)
