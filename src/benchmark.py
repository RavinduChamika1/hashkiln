# Copyright (c) 2026 Ravindu Chamika | MIT License | Author details: see src/about.py
"""
benchmark.py - DEMO 2: Speed benchmark.

Why speed matters: an attacker with a stolen database just guesses passwords and
hashes each guess. The faster the hash, the more guesses per second they can make.
For PASSWORD storage, slow is good.

NOTE: Python measures far fewer hashes/second than a real attacker's GPUs. The
exact numbers are not the point, the HUGE GAP between fast and slow hashes is.
"""

import math
import time
from dataclasses import dataclass

from rich import box
from rich.table import Table

import algorithms as alg
from ui import FAST_COLOR, SLOW_COLOR, console, heading, humanize_seconds, lesson, pause

GUESSES = 1_000_000_000   # "how long to try one billion guesses?"


@dataclass
class BenchResult:
    name: str
    family: str          # "fast" or "slow"
    per_second: float
    seconds_each: float
    slowdown: float = 1.0


def measure(func, budget_seconds: float, min_runs: int = 2) -> tuple[float, float]:
    """
    Call func() repeatedly for about `budget_seconds` (at least `min_runs` times).
    Returns (calls per second, seconds per call).
    """
    runs = 0
    start = time.perf_counter()
    while True:
        func()
        runs += 1
        elapsed = time.perf_counter() - start
        if elapsed >= budget_seconds and runs >= min_runs:
            break
    return runs / elapsed, elapsed / runs


def run_benchmark(fast: bool = False, progress_callback=None) -> list[BenchResult]:
    """Time each algorithm and return results (slowdown is relative to MD5)."""
    budget_fast = 0.15 if fast else 0.4     # fast hashes finish many runs quickly
    budget_slow = 0.6 if fast else 1.5      # slow hashes need a few runs to measure

    tests = [
        ("MD5",                    "fast", lambda: alg.md5_hash("password123"), budget_fast),
        ("SHA-256",                "fast", lambda: alg.sha256_hash("password123"), budget_fast),
        (f"bcrypt (cost {alg.BCRYPT_COST})", "slow", lambda: alg.bcrypt_hash("password123"), budget_slow),
        ("Argon2id", "slow", lambda: alg.argon2_hash("password123"), budget_slow),
    ]

    results = []
    for name, family, func, budget in tests:
        if progress_callback:
            progress_callback(name)
        per_sec, each = measure(func, budget)
        results.append(BenchResult(name, family, per_sec, each))

    baseline = results[0].per_second           # MD5 is the reference
    for r in results:
        r.slowdown = baseline / r.per_second
    return results


def _bar(value: float, maximum: float, width: int = 24) -> str:
    """Log-scale bar so a 100,000x gap is still visible on screen."""
    filled = int(width * math.log10(max(value, 1)) / math.log10(maximum))
    return "█" * max(filled, 1)


def run(fast: bool = False) -> None:
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

    heading("DEMO 2 - Speed benchmark: why FAST hashes are dangerous",
            "How many guesses per second could an attacker make on this one CPU core?")

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(bar_width=24),
                  console=console, transient=True) as progress:
        task = progress.add_task("Starting...", total=None)
        results = run_benchmark(fast, lambda name: progress.update(task, description=f"Timing {name} ..."))

    peak = max(r.per_second for r in results)
    table = Table(box=box.ROUNDED, title="Hashes per second (log-scale bars)")
    table.add_column("Algorithm", style="bold")
    table.add_column("Guesses / sec", justify="right")
    table.add_column("Speed", no_wrap=True)
    table.add_column("vs MD5", justify="right")
    table.add_column("1 billion guesses would take", justify="right")
    for r in results:
        color = FAST_COLOR if r.family == "fast" else SLOW_COLOR
        table.add_row(
            r.name, f"{r.per_second:,.1f}", f"[{color}]{_bar(r.per_second, peak)}[/{color}]",
            "baseline" if r is results[0] else ("about the same" if r.slowdown < 3 else f"{r.slowdown:,.0f}x slower"),
            humanize_seconds(GUESSES / r.per_second),
        )
    console.print(table)

    lesson("A fast hash lets an attacker try [bold red]huge numbers of guesses[/bold red] per second.\n"
           "bcrypt and Argon2 are slow ON PURPOSE (Argon2 also needs lots of memory), so every\n"
           "guess is expensive. [bold]Slow is a feature for passwords.[/bold]\n"
           "[dim]Real attackers use GPUs that are far faster at MD5/SHA than this Python test.[/dim]")
    pause(fast)
