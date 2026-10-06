# Copyright (c) 2026 Ravindu Chamika | MIT License | Author details: see src/about.py
"""
salt_demo.py - DEMO 3: What a SALT does.

A salt is a random value added to the password BEFORE hashing, unique per user.
It is stored next to the hash (it is not secret). It defeats two attacks:
  1. Spotting users who share a password (identical hashes give them away)
  2. Pre-computed lookup tables ("rainbow tables") built from common passwords
"""

from rich import box
from rich.table import Table

import algorithms as alg
from samples import COMMON_PASSWORDS
from ui import FAST_COLOR, SLOW_COLOR, console, heading, lesson, pause, short

SHARED_PASSWORD = "sunshine"     # two different users happen to pick the same password


def compare_unsalted_vs_salted() -> dict:
    """Pure logic (easy to test): hash the same password for two users, both ways."""
    unsalted_a, unsalted_b = alg.sha256_hash(SHARED_PASSWORD), alg.sha256_hash(SHARED_PASSWORD)
    bcrypt_a, bcrypt_b = alg.bcrypt_hash(SHARED_PASSWORD, cost=10), alg.bcrypt_hash(SHARED_PASSWORD, cost=10)
    argon_a, argon_b = alg.argon2_hash(SHARED_PASSWORD), alg.argon2_hash(SHARED_PASSWORD)
    return {
        "unsalted": (unsalted_a, unsalted_b),
        "bcrypt": (bcrypt_a, bcrypt_b),
        "argon2": (argon_a, argon_b),
    }


def lookup_table_attack(stored_hash: str) -> str | None:
    """
    Pre-computed lookup table: hash every common password ONCE, then any stolen
    UNSALTED hash is found instantly with a dictionary lookup.
    """
    table = {alg.sha256_hash(word): word for word in COMMON_PASSWORDS}
    return table.get(stored_hash)


def run(fast: bool = False) -> None:
    heading("DEMO 3 - Salt: why identical passwords must not look identical",
            f"Two users, alice and bob, both chose the password '{SHARED_PASSWORD}'.")

    data = compare_unsalted_vs_salted()

    # ---- Part A: same password, same hash? -----------------------------------
    table = Table(box=box.ROUNDED, title="What the stolen database shows")
    table.add_column("Method", style="bold")
    table.add_column("alice's stored value")
    table.add_column("bob's stored value")
    table.add_column("Identical?", justify="center")

    ua, ub = data["unsalted"]
    table.add_row("SHA-256, no salt", f"[{FAST_COLOR}]{short(ua, 28)}[/{FAST_COLOR}]",
                  f"[{FAST_COLOR}]{short(ub, 28)}[/{FAST_COLOR}]", "[red]YES - they share a password![/red]")
    ba, bb = data["bcrypt"]
    table.add_row("bcrypt (salted)", f"[{SLOW_COLOR}]{short(ba[7:], 28)}[/{SLOW_COLOR}]",
                  f"[{SLOW_COLOR}]{short(bb[7:], 28)}[/{SLOW_COLOR}]", "[green]No[/green]")
    aa, ab = data["argon2"]
    table.add_row("Argon2id (salted)", f"[{SLOW_COLOR}]{short(alg.extract_argon2_parts(aa)['hash'], 28)}[/{SLOW_COLOR}]",
                  f"[{SLOW_COLOR}]{short(alg.extract_argon2_parts(ab)['hash'], 28)}[/{SLOW_COLOR}]", "[green]No[/green]")
    console.print(table)

    # ---- Part B: where is the salt stored? -----------------------------------
    console.print("\n[bold]Where is the salt? Inside the stored string (it is not a secret):[/bold]")
    console.print(f"  bcrypt   : [dim]$2b$12$[/dim][yellow]{alg.extract_bcrypt_salt(ba)}[/yellow][dim]<hash>[/dim]   "
                  f"[dim](salt = 22 characters)[/dim]")
    parts = alg.extract_argon2_parts(aa)
    console.print(f"  Argon2id : [dim]${parts['algorithm']}${parts['version']}${parts['params']}$[/dim]"
                  f"[yellow]{parts['salt']}[/yellow][dim]$<hash>[/dim]")
    console.print(f"  [dim]alice's and bob's salts differ: {alg.extract_bcrypt_salt(ba)} vs {alg.extract_bcrypt_salt(bb)}[/dim]")

    # ---- Part C: lookup-table attack -----------------------------------------
    console.print("\n[bold]Lookup-table attack[/bold] "
                  "(an attacker pre-hashes common passwords, then matches the stolen hashes)")
    found = lookup_table_attack(ua)
    console.print(f"  Unsalted SHA-256 : [red]cracked instantly -> '{found}'[/red]")
    found = lookup_table_attack(ba)
    console.print(f"  Salted bcrypt    : [green]not in the table ({'no match' if found is None else found}). "
                  f"The salt makes the table useless.[/green]")

    lesson("A salt is [bold]random and unique per password[/bold]. It stops hash-sharing from leaking\n"
           "who reuses a password and makes pre-computed tables useless. Never write your\n"
           "own salting: bcrypt and Argon2 create and store a random salt for you.")
    pause(fast)
