# Copyright (c) 2026 Ravindu Chamika | MIT License | Author details: see src/about.py
"""
algorithms.py - One small, clear wrapper for every hashing algorithm in the lab.

TWO FAMILIES (the main lesson of Week 2)
----------------------------------------
FAST hashes   MD5, SHA-1, SHA-256, SHA-512
              Built for speed (file checks, signatures). An attacker can try
              BILLIONS of guesses per second. NEVER use them to store passwords.

SLOW hashes   bcrypt, Argon2id
              Built for passwords. They are slow ON PURPOSE (and Argon2 also uses
              lots of memory), so each guess is expensive. Both create a random
              SALT for you and store it inside the output string.

Safe settings used here
-----------------------
Argon2id: 19 MiB memory, 2 iterations, 1 thread   (OWASP minimum profile)
bcrypt  : cost (work factor) 12                   (OWASP minimum is 10)
Always re-check the current OWASP Password Storage Cheat Sheet before using
these numbers in a real project.
"""

import hashlib
import hmac

import bcrypt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

# --------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------
BCRYPT_COST = 12                 # work factor: each +1 doubles the time
BCRYPT_MAX_BYTES = 72            # bcrypt cannot use more than 72 bytes
ARGON2_MEMORY_KIB = 19456        # 19 MiB
ARGON2_TIME_COST = 2             # iterations
ARGON2_PARALLELISM = 1           # threads

# One reusable Argon2id hasher (type=ID is the default and the recommended one)
_argon2 = PasswordHasher(
    time_cost=ARGON2_TIME_COST,
    memory_cost=ARGON2_MEMORY_KIB,
    parallelism=ARGON2_PARALLELISM,
)


class PasswordTooLongError(ValueError):
    """bcrypt only reads the first 72 bytes, so we refuse longer inputs clearly."""


# --------------------------------------------------------------------------
# FAST hashes (for learning and comparison only, NOT for storing passwords)
# --------------------------------------------------------------------------
def md5_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def sha1_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def sha256_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha512_hash(text: str) -> str:
    return hashlib.sha512(text.encode("utf-8")).hexdigest()


# Name -> function lookup used by the explorer and the benchmark
FAST_HASHES = {
    "MD5": md5_hash,
    "SHA-1": sha1_hash,
    "SHA-256": sha256_hash,
    "SHA-512": sha512_hash,
}


# --------------------------------------------------------------------------
# SLOW, salted hashes (the right tools for passwords)
# --------------------------------------------------------------------------
def bcrypt_hash(password: str, cost: int = BCRYPT_COST) -> str:
    """Hash with bcrypt. A fresh random salt is created and stored in the result."""
    raw = password.encode("utf-8")
    if len(raw) > BCRYPT_MAX_BYTES:
        raise PasswordTooLongError(
            f"bcrypt only uses the first {BCRYPT_MAX_BYTES} bytes "
            f"(got {len(raw)}). Use Argon2id, or shorten the password."
        )
    return bcrypt.hashpw(raw, bcrypt.gensalt(rounds=cost)).decode("ascii")


def bcrypt_verify(password: str, stored: str) -> bool:
    """True if the password matches the stored bcrypt hash."""
    raw = password.encode("utf-8")
    if len(raw) > BCRYPT_MAX_BYTES:
        return False
    try:
        return bcrypt.checkpw(raw, stored.encode("ascii"))
    except ValueError:
        return False


def argon2_hash(password: str) -> str:
    """Hash with Argon2id. Salt and settings are stored inside the result."""
    return _argon2.hash(password)


def argon2_verify(password: str, stored: str) -> bool:
    """True if the password matches the stored Argon2 hash."""
    try:
        return _argon2.verify(stored, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def argon2_needs_rehash(stored: str) -> bool:
    """True if the stored hash used weaker settings than today's (upgrade on next login)."""
    return _argon2.check_needs_rehash(stored)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def safe_equal(a: str, b: str) -> bool:
    """
    Compare two strings in CONSTANT time.
    A normal '==' stops at the first different character, and that tiny timing
    difference can leak information. compare_digest avoids this.
    """
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def bit_difference(hex_a: str, hex_b: str) -> tuple[int, int]:
    """Return (bits that differ, total bits) between two hex digests of equal length."""
    a, b = int(hex_a, 16), int(hex_b, 16)
    total = len(hex_a) * 4
    return bin(a ^ b).count("1"), total


def extract_bcrypt_salt(stored: str) -> str:
    """bcrypt format: $2b$12$<22-char salt><31-char hash>. Return the salt part."""
    return stored[7:29]


def extract_argon2_parts(stored: str) -> dict:
    """Argon2 format: $argon2id$v=19$m=19456,t=2,p=1$<salt>$<hash>."""
    _, algo, version, params, salt, digest = stored.split("$")
    return {"algorithm": algo, "version": version, "params": params, "salt": salt, "hash": digest}
