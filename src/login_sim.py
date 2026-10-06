# Copyright (c) 2026 Ravindu Chamika | MIT License | Author details: see src/about.py
"""
login_sim.py - DEMO 5: Sign-up and login simulator (the "check-in").

Shows exactly what a website does:
  SIGN UP : hash the password (with a salt) and store ONLY the hash.
  LOG IN  : hash what the user typed the same way and compare with the stored hash.
The real password is never stored. Everything lives in memory and disappears on exit.
"""

import getpass

from rich import box
from rich.panel import Panel
from rich.table import Table

import algorithms as alg
from ui import console, heading, lesson, pause, short

ALGORITHMS = {
    "1": ("argon2id", "Argon2id  (recommended)"),
    "2": ("bcrypt",   "bcrypt    (good, older)"),
    "3": ("md5",      "MD5       (INSECURE - for comparison only)"),
}


# --------------------------------------------------------------------------
# Core logic (no printing, so it can be unit-tested)
# --------------------------------------------------------------------------
def make_record(password: str, algorithm: str) -> dict:
    """Hash a password and return what the website would store."""
    if algorithm == "argon2id":
        stored = alg.argon2_hash(password)
    elif algorithm == "bcrypt":
        stored = alg.bcrypt_hash(password)
    elif algorithm == "md5":
        stored = alg.md5_hash(password)
    else:
        raise ValueError(f"unknown algorithm: {algorithm}")
    return {"algorithm": algorithm, "stored": stored}


def check_password(password: str, record: dict) -> bool:
    """Re-hash the typed password and compare with the stored record."""
    algorithm, stored = record["algorithm"], record["stored"]
    if algorithm == "argon2id":
        return alg.argon2_verify(password, stored)
    if algorithm == "bcrypt":
        return alg.bcrypt_verify(password, stored)
    return alg.safe_equal(alg.md5_hash(password), stored)   # constant-time compare


# --------------------------------------------------------------------------
# Interactive part
# --------------------------------------------------------------------------
def _ask_password(prompt: str) -> str:
    return getpass.getpass(prompt)


def _sign_up(users: dict) -> None:
    name = console.input("Choose a username: ").strip()
    if not name:
        console.print("[red]Username cannot be empty.[/red]")
        return
    if name in users:
        console.print("[red]That username already exists.[/red]")
        return

    console.print("Pick how the website should store the password:")
    for key, (_, label) in ALGORITHMS.items():
        console.print(f"  {key}. {label}")
    algorithm = ALGORITHMS.get(console.input("Choice [1]: ").strip() or "1", ALGORITHMS["1"])[0]

    password = _ask_password("Choose a password (hidden): ")
    if not password:
        console.print("[red]Password cannot be empty.[/red]")
        return
    try:
        with console.status("Hashing ..."):
            users[name] = make_record(password, algorithm)
    except alg.PasswordTooLongError as exc:
        console.print(f"[red]{exc}[/red]")
        return

    console.print(Panel(
        f"[bold]Account created for '{name}'[/bold]\n\n"
        f"1. Your password was [bold]hashed[/bold] with {algorithm}\n"
        f"2. Only this was stored: [cyan]{short(users[name]['stored'], 60)}[/cyan]\n"
        f"3. Your real password was [bold]discarded[/bold]",
        border_style="green", title="SIGN UP"))


def _log_in(users: dict) -> None:
    name = console.input("Username: ").strip()
    record = users.get(name)
    password = _ask_password("Password (hidden): ")
    # Even for unknown users, do the work, so response time does not reveal which usernames exist
    if record is None:
        alg.argon2_verify(password, alg.argon2_hash("dummy"))
        ok = False
    else:
        console.print("[dim]1. Fetch stored record   2. Re-hash typed password with the stored salt   "
                      "3. Compare in constant time[/dim]")
        with console.status("Verifying ..."):
            ok = check_password(password, record)
    if ok:
        console.print(Panel("[bold green]Access granted[/bold green]: the hashes matched.", border_style="green", title="LOG IN"))
        if record["algorithm"] == "argon2id" and alg.argon2_needs_rehash(record["stored"]):
            console.print("[yellow]Note: the stored hash uses old settings. A real site would re-hash it now.[/yellow]")
    else:
        console.print(Panel("[bold red]Access denied[/bold red]: wrong username or password.", border_style="red", title="LOG IN"))


def _show_database(users: dict) -> None:
    if not users:
        console.print("[yellow]No users yet. Sign up first.[/yellow]")
        return
    table = Table(box=box.ROUNDED, title="What an attacker would steal (no passwords in it)")
    table.add_column("Username", style="bold")
    table.add_column("Algorithm")
    table.add_column("Stored value")
    for name, rec in users.items():
        table.add_row(name, rec["algorithm"], short(rec["stored"], 64))
    console.print(table)


def run(fast: bool = False) -> None:
    heading("DEMO 5 - Sign-up & login simulator",
            "Create an account, log in, and see what the website really stores. (In memory only.)")
    users: dict = {}
    while True:
        console.print("\n[bold]1[/bold] Sign up   [bold]2[/bold] Log in   [bold]3[/bold] View stored database   [bold]0[/bold] Back")
        try:
            choice = console.input("Choose: ").strip()
        except EOFError:
            break
        if choice == "1":
            _sign_up(users)
        elif choice == "2":
            _log_in(users)
        elif choice == "3":
            _show_database(users)
        elif choice == "0":
            break
        else:
            console.print("[red]Please choose 0-3.[/red]")

    lesson("The site never keeps your real password. It keeps a salted hash and only checks whether\n"
           "two hashes match. If the database is stolen, a [bold]slow salted hash[/bold] protects every user.")
