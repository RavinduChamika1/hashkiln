# Copyright (c) 2026 Ravindu Chamika | MIT License | Author details: see src/about.py
"""
cli.py - HashKiln: Password Hashing Lab (Week 2 of 52 Weeks of Security)

PROGRAM FLOW
------------
  Main menu -> pick a demo -> read the result and the lesson -> back to the menu

  1  Hash explorer & avalanche effect      (what a hash is)
  2  Speed benchmark                       (why fast hashes are dangerous)
  3  Salt demo                             (why salts matter)
  4  Dictionary attack on a fake database  (see the difference in action)
  5  Sign-up & login simulator             (how websites really check passwords)
  6  Guided tour                           (demos 1-4 in order)

Run:
    python src/cli.py                  # interactive menu
    python src/cli.py --run all        # guided tour of demos 1-4
    python src/cli.py --run benchmark  # one demo directly
    python src/cli.py --fast           # shorter timings, no pauses
"""

import argparse
import sys

from rich.panel import Panel

import about
import attack_demo
import benchmark
import explorer
import login_sim
import salt_demo
from ui import console

# Menu key -> (label, function)
DEMOS = {
    "1": ("Hash explorer & avalanche effect", explorer.run),
    "2": ("Speed benchmark: fast vs slow hashes", benchmark.run),
    "3": ("Salt demo", salt_demo.run),
    "4": ("Dictionary attack on a fake database", attack_demo.run),
    "5": ("Sign-up & login simulator", login_sim.run),
}
# Names usable with --run
NAMES = {"explorer": "1", "benchmark": "2", "salt": "3", "attack": "4", "login": "5"}


def show_banner() -> None:
    console.print(Panel.fit(
        f"[bold orange1]{about.APP_NAME}[/bold orange1]  [bold]{about.APP_TAGLINE}[/bold]\n"
        f"[dim]{about.SERIES}[/dim]\n\n"
        "Learn why password storage matters: MD5, SHA, bcrypt, Argon2 and salts.\n"
        "Everything runs on your computer. No internet, no API key, nothing is saved.\n\n"
        f"[dim]© {about.YEAR} {about.AUTHOR} · {about.LICENSE_NAME}\n"
        f"LinkedIn: {about.LINKEDIN}[/dim]",
        border_style="orange1", padding=(1, 3)))


def guided_tour(fast: bool) -> None:
    """Run demos 1-4 in order (the login simulator is interactive, so it is separate)."""
    for key in ("1", "2", "3", "4"):
        DEMOS[key][1](fast)


def menu(fast: bool) -> None:
    while True:
        console.print("\n[bold]Choose a demo[/bold]")
        for key, (label, _) in DEMOS.items():
            console.print(f"  [bold orange1]{key}[/bold orange1]  {label}")
        console.print("  [bold orange1]6[/bold orange1]  Guided tour (demos 1-4)")
        console.print("  [bold orange1]0[/bold orange1]  Exit")
        try:
            choice = console.input("\nYour choice: ").strip()
        except EOFError:
            return
        if choice == "0":
            return
        if choice == "6":
            guided_tour(fast)
        elif choice in DEMOS:
            DEMOS[choice][1](fast)
        else:
            console.print("[red]Please enter a number from 0 to 6.[/red]")


def main() -> None:
    parser = argparse.ArgumentParser(description="HashKiln - password hashing lab")
    parser.add_argument("--run", choices=[*NAMES, "all"], help="run one demo (or 'all') without the menu")
    parser.add_argument("--fast", action="store_true", help="shorter timings and no pauses")
    args = parser.parse_args()

    show_banner()
    try:
        if args.run == "all":
            guided_tour(args.fast)
        elif args.run:
            DEMOS[NAMES[args.run]][1](args.fast)
        else:
            menu(args.fast)
    except KeyboardInterrupt:
        console.print("\n[dim]Cancelled.[/dim]")

    console.print(f"\n[orange1]Remember: never store passwords with plain MD5 or SHA. "
                  f"Use Argon2id or bcrypt.[/orange1]")
    console.print(f"[dim]Built by {about.AUTHOR} · {about.LINKEDIN}[/dim]")


if __name__ == "__main__":
    sys.exit(main())
