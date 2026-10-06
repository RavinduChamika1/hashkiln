# Copyright (c) 2026 Ravindu Chamika | MIT License | Author details: see src/about.py
"""
ui.py - Shared look and feel (colours, headings, pauses, number formatting).
Keeping this in one place makes every demo look consistent.
"""

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

console = Console()

# Colour for each algorithm family
FAST_COLOR = "red"      # fast hashes = dangerous for passwords
SLOW_COLOR = "green"    # slow salted hashes = right tool


def heading(title: str, subtitle: str = "") -> None:
    """Big section heading used at the start of each demo."""
    console.print()
    console.print(Rule(f"[bold cyan]{title}[/bold cyan]", style="cyan"))
    if subtitle:
        console.print(f"[dim]{subtitle}[/dim]")
    console.print()


def lesson(text: str, title: str = "What this shows") -> None:
    """A highlighted box that states the key takeaway of a demo."""
    console.print(Panel(text, title=f"[bold yellow]{title}[/bold yellow]", border_style="yellow", padding=(0, 2)))


def pause(fast: bool) -> None:
    """Wait for Enter so the student can read. Skipped in --fast mode."""
    if not fast:
        try:
            console.input("\n[dim]Press Enter to continue...[/dim]")
        except EOFError:
            pass


def humanize_seconds(seconds: float) -> str:
    """Turn a number of seconds into a friendly unit (e.g. '3.2 hours')."""
    if seconds < 1:
        return f"{seconds * 1000:.1f} ms"
    units = [("seconds", 60), ("minutes", 60), ("hours", 24), ("days", 365), ("years", 1000)]
    value = seconds
    for name, size in units:
        if value < size:
            return f"{value:,.1f} {name}"
        value /= size
    return f"{value:,.1f} millennia"


def short(text: str, keep: int = 36) -> str:
    """Shorten long hashes for display, keeping the start."""
    return text if len(text) <= keep else text[:keep] + "..."
