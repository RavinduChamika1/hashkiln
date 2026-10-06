# Copyright (c) 2026 Ravindu Chamika | MIT License | Author details: see src/about.py
"""
attack_demo.py - DEMO 4: A mini dictionary attack on a FAKE stolen database.

SAFETY: this only attacks hashes the program creates itself from the fake users in
samples.py. Never attack real accounts or data you do not own.

The attacker has a stolen database and a wordlist. For each guess they hash it and
compare. We give the attacker the SAME time budget against each storage method and
see how many accounts fall.
"""

import time
from dataclasses import dataclass

from rich import box
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn
from rich.table import Table

import algorithms as alg
from samples import COMMON_PASSWORDS, FAKE_USERS
from ui import console, heading, humanize_seconds, lesson, pause


@dataclass
class AttackResult:
    method: str
    cracked: dict          # username -> password found
    total_users: int
    guesses: int           # hashing operations performed
    seconds: float
    finished: bool         # True if the whole wordlist was tried for every user

    @property
    def guesses_per_second(self) -> float:
        return self.guesses / self.seconds if self.seconds else 0.0


def build_database(method: str) -> dict:
    """Create the fake 'stolen' database: username -> stored hash."""
    if method == "md5":
        return {user: alg.md5_hash(pw) for user, pw in FAKE_USERS}
    if method == "bcrypt":
        return {user: alg.bcrypt_hash(pw) for user, pw in FAKE_USERS}
    if method == "argon2":
        return {user: alg.argon2_hash(pw) for user, pw in FAKE_USERS}
    raise ValueError(f"unknown method: {method}")


def attack(method: str, database: dict, budget_seconds: float, tick=None) -> AttackResult:
    """
    Dictionary attack with a time budget.
    * Unsalted MD5   : hash each guess ONCE and compare to every user (one pass cracks all).
    * Salted bcrypt/Argon2: every user has a different salt, so each guess must be
      re-hashed PER USER. That multiplies the attacker's work.
    """
    cracked, guesses = {}, 0
    start = time.perf_counter()
    finished = True

    for word in COMMON_PASSWORDS:
        if time.perf_counter() - start >= budget_seconds:
            finished = False
            break
        remaining = {u: h for u, h in database.items() if u not in cracked}
        if not remaining:
            break

        if method == "md5":
            guess_hash = alg.md5_hash(word)       # one hash serves all users
            guesses += 1
            for user, stored in remaining.items():
                if alg.safe_equal(guess_hash, stored):
                    cracked[user] = word
        else:
            verify = alg.bcrypt_verify if method == "bcrypt" else alg.argon2_verify
            for user, stored in remaining.items():  # one expensive hash per user
                if time.perf_counter() - start >= budget_seconds:
                    finished = False
                    break
                guesses += 1
                if verify(word, stored):
                    cracked[user] = word
        if not finished:
            break
        if tick:
            tick()

    return AttackResult(method, cracked, len(database), guesses, time.perf_counter() - start, finished)


def run(fast: bool = False) -> None:
    budget = 2.5 if fast else 5.0
    heading("DEMO 4 - Dictionary attack on a fake stolen database",
            f"Wordlist: {len(COMMON_PASSWORDS)} common passwords | Users: {len(FAKE_USERS)} | "
            f"Attacker time budget per method: {budget:.0f}s")
    console.print("[dim]Only fake hashes created by this program are attacked.[/dim]\n")

    methods = [
        ("md5", "Unsalted MD5"),
        ("bcrypt", f"Salted bcrypt (cost {alg.BCRYPT_COST})"),
        ("argon2", "Salted Argon2id"),
    ]

    results = []
    for key, label in methods:
        with console.status(f"Building fake database ({label}) ..."):
            database = build_database(key)
        with Progress(TextColumn("{task.description}"), BarColumn(bar_width=30),
                      TextColumn("{task.completed}/{task.total} words"), TimeElapsedColumn(),
                      console=console, transient=False) as progress:
            task = progress.add_task(f"Attacking {label:<26}", total=len(COMMON_PASSWORDS))
            result = attack(key, database, budget, tick=lambda: progress.advance(task))
            progress.update(task, completed=len(COMMON_PASSWORDS) if result.finished else progress.tasks[0].completed)
        result.method = label
        results.append(result)

    console.print()
    table = Table(box=box.ROUNDED, title="Attack results")
    table.add_column("Storage method", style="bold")
    table.add_column("Accounts cracked", justify="center")
    table.add_column("Guesses / sec", justify="right")
    table.add_column("Time taken", justify="right")
    table.add_column("Outcome")
    for r in results:
        n = len(r.cracked)
        colour = "red" if n == r.total_users else ("yellow" if n else "green")
        outcome = ("[red]Whole database cracked[/red]" if n == r.total_users
                   else "[green]Attacker ran out of time[/green]" if not r.finished
                   else "[yellow]Partly cracked[/yellow]")
        table.add_row(r.method, f"[{colour}]{n}/{r.total_users}[/{colour}]",
                      f"{r.guesses_per_second:,.0f}", humanize_seconds(r.seconds), outcome)
    console.print(table)

    slow = results[1]
    if slow.guesses_per_second:
        full = len(COMMON_PASSWORDS) * len(FAKE_USERS) / slow.guesses_per_second
        console.print(f"\n[dim]Trying this whole {len(COMMON_PASSWORDS)}-word list against all "
                      f"{len(FAKE_USERS)} salted users would take about {humanize_seconds(full)} "
                      f"with bcrypt. Real wordlists have billions of entries.[/dim]")

    lesson("Same passwords, same attacker, same wordlist. The only difference is HOW they were stored.\n"
           "Unsalted MD5 falls almost instantly. Salted slow hashes force the attacker to pay a high\n"
           "price [bold]per guess, per user[/bold]. Even so, [bold]weak passwords can still fall[/bold], so strong\n"
           "passwords and good hashing work together.")
    pause(fast)
