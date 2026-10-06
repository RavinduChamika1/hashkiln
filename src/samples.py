# Copyright (c) 2026 Ravindu Chamika | MIT License | Author details: see src/about.py
"""
samples.py - Built-in SAMPLE data used by the demos.

Everything here is fake or very common. The demos only attack hashes that this
program creates itself, never anyone's real data.
"""

# A tiny "attacker wordlist" of very common passwords (real ones are in the billions).
# The order matters: the attacker tries them from top to bottom.
COMMON_PASSWORDS = [
    "123456", "password", "12345678", "qwerty", "123456789", "12345", "1234", "111111",
    "1234567", "dragon", "123123", "baseball", "abc123", "football", "monkey", "letmein",
    "696969", "shadow", "master", "666666", "qwertyuiop", "123321", "mustang", "1234567890",
    "michael", "654321", "superman", "1qaz2wsx", "7777777", "121212", "000000", "qazwsx",
    "123qwe", "killer", "trustno1", "jordan", "jennifer", "zxcvbnm", "asdfgh", "hunter",
    "buster", "soccer", "harley", "batman", "andrew", "tigger", "sunshine", "iloveyou",
]

# Fake users for the attack demo. Their passwords are deliberately late in the list.
FAKE_USERS = [
    ("alice", "tigger"),
    ("bob", "sunshine"),
    ("carol", "iloveyou"),
    ("dave", "batman"),
]
