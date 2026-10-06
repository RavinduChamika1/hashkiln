# Copyright (c) 2026 Ravindu Chamika | MIT License | Author details: see src/about.py
"""
explorer.py - DEMO 1: Hash explorer and the avalanche effect.

A hash function turns ANY input into a fixed-size scrambled output.
  * Same input  -> always the same output   (so we can check a password later)
  * One tiny change -> a completely different output (the AVALANCHE effect)
  * Output -> input is impossible to reverse directly (one-way)
"""

from rich import box
from rich.table import Table

import algorithms as alg
from ui import FAST_COLOR, console, heading, lesson, pause, short


def explore(text_a: str, text_b: str) -> dict:
    """Pure logic (easy to test): hash two inputs and measure how different they are."""
    results = {}
    for name, func in alg.FAST_HASHES.items():
        hash_a, hash_b = func(text_a), func(text_b)
        diff, total = alg.bit_difference(hash_a, hash_b)
        results[name] = {
            "a": hash_a, "b": hash_b, "bits": len(hash_a) * 4,
            "diff": diff, "total": total, "percent": 100 * diff / total,
        }
    return results


def run(fast: bool = False) -> None:
    heading("DEMO 1 - Hash explorer & the avalanche effect",
            "Same input = same hash. One tiny change = a completely different hash.")

    text_a = "password"
    if not fast:
        typed = console.input("Text to hash [dim](Enter for 'password')[/dim]: ").strip()
        text_a = typed or text_a
    # Change just ONE character (flip the case of the first letter, or add a '!')
    text_b = text_a[0].swapcase() + text_a[1:] if text_a[0].swapcase() != text_a[0] else text_a + "!"

    results = explore(text_a, text_b)

    table = Table(box=box.ROUNDED, title=f"Hashing  [bold]'{text_a}'[/bold]  vs  [bold]'{text_b}'[/bold]")
    table.add_column("Algorithm", style="bold")
    table.add_column("Size", justify="right")
    table.add_column(f"Hash of '{text_a}'")
    table.add_column("Bits changed", justify="right")
    for name, r in results.items():
        table.add_row(name, f"{r['bits']} bits", f"[{FAST_COLOR}]{short(r['a'], 40)}[/{FAST_COLOR}]",
                      f"{r['diff']}/{r['total']}  ({r['percent']:.0f}%)")
    console.print(table)

    console.print(f"\n[bold]Full SHA-256 comparison[/bold]")
    console.print(f"  '{text_a}' -> [cyan]{results['SHA-256']['a']}[/cyan]")
    console.print(f"  '{text_b}' -> [cyan]{results['SHA-256']['b']}[/cyan]")

    lesson("About half of the bits flip when you change a SINGLE character. This is the\n"
           "[bold]avalanche effect[/bold]: you cannot tell two similar inputs are related.\n"
           "But these hashes are FAST, which is exactly why they are wrong for passwords.")
    pause(fast)
