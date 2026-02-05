import subprocess

import typer
from rich.console import Console
from rich.table import Table

from src import arduino_config as config
from src.board import check_arduino_cli

console = Console()


def show_libraries() -> None:
    """Display installed libraries."""
    check_arduino_cli()
    result = subprocess.run(
        ["arduino-cli", "lib", "list"],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    if result.returncode != 0:
        console.print("[bold red]Error running arduino-cli lib list:[/bold red]")
        console.print(result.stderr or result.stdout)
        raise typer.Exit(result.returncode)

    console.print(result.stdout)


def show_cores() -> None:
    """Display installed cores/platforms."""
    check_arduino_cli()
    result = subprocess.run(
        ["arduino-cli", "core", "list"],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    if result.returncode != 0:
        console.print("[bold red]Error running arduino-cli core list:[/bold red]")
        console.print(result.stderr or result.stdout)
        raise typer.Exit(result.returncode)

    console.print(result.stdout)


def show_config() -> None:
    """Display current tool configuration."""
    table = Table(title="Arduino CLI Tool Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("FQBN", config.get_fqbn())
    table.add_row("Upload Speed", f"{config.get_upload_speed()} baud")
    table.add_row("Monitor Baudrate", f"{config.get_baudrate()} baud")

    console.print(table)


def show_version() -> None:
    """Display arduino-cli version."""
    check_arduino_cli()
    result = subprocess.run(
        ["arduino-cli", "version"],
        capture_output=True,
        text=True,
        check=False,
        timeout=5,
    )
    if result.returncode != 0:
        console.print("[bold red]Error running arduino-cli version:[/bold red]")
        console.print(result.stderr or result.stdout)
        raise typer.Exit(result.returncode)

    console.print(result.stdout.strip())
