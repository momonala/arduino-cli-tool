import typer
from rich.console import Console

from src import arduino_config as config
from src import board
from src import cli
from src import info

app = typer.Typer(help="Simplified CLI wrapper for arduino-cli")
console = Console()

show_app = typer.Typer(help="Show information about boards, libraries, cores, and config")
app.add_typer(show_app, name="show")


def handle_exit(exit_code: int) -> None:
    """Raise typer.Exit(exit_code) if non-zero."""
    if exit_code != 0:
        raise typer.Exit(exit_code)


@app.command(name="compile")
def compile_cmd(
    fqbn: str | None = typer.Option(None, "--fqbn", help="Board FQBN (e.g. esp32:esp32:esp32)"),
    path: str = typer.Option(".", "--path", "-p", help="Sketch path"),
) -> None:
    """Compile Arduino sketch."""
    handle_exit(cli.compile(config.get_fqbn(fqbn), path))


@app.command(name="upload")
def upload_cmd(
    fqbn: str | None = typer.Option(None, "--fqbn", help="Board FQBN"),
    port: str | None = typer.Option(None, "--port", help="Serial port (auto-detected if omitted)"),
    speed: int | None = typer.Option(None, "--speed", help="Upload speed in baud"),
    path: str = typer.Option(".", "--path", "-p", help="Sketch path"),
) -> None:
    """Upload sketch to board."""
    selected = board.select_board(port)
    handle_exit(cli.upload(config.get_fqbn(fqbn), selected.port, config.get_upload_speed(speed), path))


@app.command(name="monitor")
def monitor_cmd(
    port: str | None = typer.Option(None, "--port", help="Serial port (auto-detected if omitted)"),
    baudrate: int | None = typer.Option(None, "--baudrate", help="Baud rate"),
) -> None:
    """Open serial monitor."""
    selected = board.select_board(port)
    handle_exit(cli.monitor(selected.port, config.get_baudrate(baudrate)))


@app.command(name="run")
def run_cmd(
    fqbn: str | None = typer.Option(None, "--fqbn", help="Board FQBN"),
    port: str | None = typer.Option(None, "--port", help="Serial port (auto-detected if omitted)"),
    speed: int | None = typer.Option(None, "--speed", help="Upload speed in baud"),
    baudrate: int | None = typer.Option(None, "--baudrate", help="Monitor baud rate"),
    path: str = typer.Option(".", "--path", "-p", help="Sketch path"),
) -> None:
    """Compile, upload, then monitor (in sequence)."""
    console.print("[bold cyan]Running: Compile → Upload → Monitor[/bold cyan]\n")

    console.print("[yellow]Step 1/3: Detecting board...[/yellow]")
    selected = board.select_board(port)
    console.print(f"[green]✓[/green] Found board: [cyan]{selected.port}[/cyan]")

    console.print("\n[yellow]Step 2/3: Compiling sketch...[/yellow]")
    handle_exit(cli.compile(config.get_fqbn(fqbn), path))
    console.print("[green]✓[/green] Compilation successful\n")

    console.print(f"[yellow]Step 3/3: Uploading to {selected.port}...[/yellow]")
    handle_exit(cli.upload(config.get_fqbn(fqbn), selected.port, config.get_upload_speed(speed), path))
    console.print("[green]✓[/green] Upload successful\n")

    console.print(f"[yellow]Starting serial monitor on {selected.port}...[/yellow]")
    handle_exit(cli.monitor(selected.port, config.get_baudrate(baudrate)))


@show_app.command(name="boards")
def show_boards_cmd() -> None:
    """Show connected USB boards."""
    board.show_usb_boards()


@show_app.command(name="libraries")
def show_libraries_cmd() -> None:
    """Show installed libraries."""
    info.show_libraries()


@show_app.command(name="cores")
def show_cores_cmd() -> None:
    """Show installed cores/platforms."""
    info.show_cores()


@show_app.command(name="config")
def show_config_cmd() -> None:
    """Show current tool configuration."""
    info.show_config()


@app.command(name="version")
def version_cmd() -> None:
    """Show arduino-cli version."""
    info.show_version()


def main() -> None:
    """CLI entry point."""
    app()


if __name__ == "__main__":
    main()
