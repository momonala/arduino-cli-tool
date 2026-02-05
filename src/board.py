import subprocess
from dataclasses import dataclass

import typer
from rich.console import Console
from rich.table import Table

console = Console()


@dataclass
class Board:
    port: str
    protocol: str
    board_type: str
    board_name: str
    fqbn: str | None = None
    raw_line: str = ""


def check_arduino_cli() -> None:
    """Ensure arduino-cli is on PATH."""
    try:
        subprocess.run(["arduino-cli", "version"], capture_output=True, check=True, timeout=5)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        console.print(
            "[bold red]Error:[/bold red] arduino-cli not found. Install it and ensure it is in your PATH."
        )
        raise typer.Exit(1) from e


def list_boards() -> tuple[list[Board], str]:
    """Return (parsed boards, raw stdout) from arduino-cli board list."""
    check_arduino_cli()
    result = subprocess.run(
        ["arduino-cli", "board", "list"],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    if result.returncode != 0:
        console.print("[bold red]Error running arduino-cli board list:[/bold red]")
        console.print(result.stderr or result.stdout)
        raise typer.Exit(result.returncode)
    return parse_board_list(result.stdout), result.stdout


def parse_board_list(output: str) -> list[Board]:
    """Parse arduino-cli board list output into Board objects."""
    lines = output.strip().split("\n")
    if len(lines) < 2:
        return []

    headers = [h.strip() for h in lines[0].split()]
    port_idx = headers.index("Port")
    protocol_idx = headers.index("Protocol") if "Protocol" in headers else 1
    type_idx = headers.index("Type")
    name_idx = headers.index("Board") if "Board" in headers else headers.index("Board Name")
    fqbn_idx = headers.index("FQBN") if "FQBN" in headers else None

    boards = []
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) <= port_idx:
            continue

        port = parts[port_idx]
        protocol = parts[protocol_idx] if len(parts) > protocol_idx else ""
        type_slice = parts[type_idx:name_idx] if type_idx < name_idx else parts[type_idx:]
        board_type = " ".join(type_slice) if type_slice else ""
        board_name = parts[name_idx] if len(parts) > name_idx else "Unknown"
        fqbn = parts[fqbn_idx] if fqbn_idx is not None and len(parts) > fqbn_idx else None

        boards.append(
            Board(
                port=port,
                protocol=protocol,
                board_type=board_type,
                board_name=board_name,
                fqbn=fqbn,
                raw_line=line,
            )
        )
    return boards


def usb_boards(boards: list[Board]) -> list[Board]:
    """Filter to boards that are USB serial ports."""
    return [b for b in boards if "USB" in b.raw_line or "USB" in b.board_type or "usbserial" in b.port]


def show_usb_boards() -> None:
    """Display connected USB boards in a clean format."""
    all_boards, _ = list_boards()
    usb = usb_boards(all_boards)

    if not usb:
        console.print("[yellow]No USB serial port boards found.[/yellow]")
        return

    table = Table(title="Connected USB Boards")
    table.add_column("Port", style="cyan")
    table.add_column("Board Name", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("FQBN", style="magenta")

    for b in usb:
        table.add_row(b.port, b.board_name, b.board_type, b.fqbn or "—")

    console.print(table)


def select_board(port: str | None = None) -> Board:
    """Pick one board: by port if given, else auto or prompt when multiple."""
    all_boards, raw_output = list_boards()
    console.print("[cyan]arduino-cli board list:[/cyan]")
    console.print(raw_output.strip())

    usb = usb_boards(all_boards)
    if not usb:
        console.print("[bold red]No USB serial port boards found.[/bold red]")
        console.print(f"[yellow]Found {len(all_boards)} board(s), none are USB serial.[/yellow]")
        console.print("\n[cyan]Connect a USB board and try again.[/cyan]")
        raise typer.Exit(1)

    if port:
        match = [b for b in usb if b.port == port]
        if not match:
            console.print(f"[bold red]Port {port} not found.[/bold red]")
            console.print(f"[yellow]Available:[/yellow] {', '.join(b.port for b in usb)}")
            raise typer.Exit(1)
        return match[0]

    if len(usb) == 1:
        return usb[0]

    typer.echo("Multiple USB boards found:")
    for i, b in enumerate(usb, 1):
        typer.echo(f"  {i}. {b.port} - {b.board_name} ({b.board_type})")
    while True:
        choice = typer.prompt("Select board (enter number)", type=int)
        if 1 <= choice <= len(usb):
            return usb[choice - 1]
        typer.echo(f"Enter a number between 1 and {len(usb)}.")
