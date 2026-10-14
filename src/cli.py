import os
import re
import subprocess
import sys
from pathlib import Path

from rich.console import Console

from src.board import check_arduino_cli

console = Console(force_terminal=True)

PROGRESS_LINE_WIDTH = 140
ESP_CORE_PREFIXES = ("esp32:", "esp8266:")
UPLOAD_PROGRESS_RE = re.compile(r"Writing at 0x[0-9a-f]+.*\d+\.\d+%")
ERROR_PATTERNS = [
    (r"fatal error:", "[bold red]"),
    (r"^Error during build:", "[bold red]"),
    (r"compilation terminated", "[red]"),
    (r":\d+:\d+: error:", "[red]"),
    (r":\d+:\d+: warning:", "[yellow]"),
]


def _style_errors(line: str) -> str:
    """Apply Rich markup to compiler error/warning lines."""
    line = line.rstrip()
    if not line:
        return line
    for pattern, style in ERROR_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return f"{style}{line}[/]"
    return line


def _is_progress_line(line: str) -> bool:
    return bool(UPLOAD_PROGRESS_RE.search(line))


def _write_progress(line: str) -> None:
    """Write a single progress line that overwrites the previous one."""
    sys.stdout.write("\r" + line[:PROGRESS_LINE_WIDTH].ljust(PROGRESS_LINE_WIDTH))
    sys.stdout.flush()


def run(args: list[str], cwd: Path | None = None) -> int:
    """Run arduino-cli with streaming output; progress lines overwrite in place."""
    check_arduino_cli()
    cmd = ["arduino-cli"] + args
    env = {**os.environ}
    env.pop("NO_COLOR", None)

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=cwd,
        env=env,
    )

    last_was_progress = False
    try:
        for line in process.stdout:
            line_clean = line.rstrip("\r\n")
            if not line_clean:
                continue
            if _is_progress_line(line_clean):
                _write_progress(line_clean)
                last_was_progress = True
            else:
                if last_was_progress:
                    sys.stdout.write("\n")
                    last_was_progress = False
                console.print(_style_errors(line_clean), markup=True, highlight=False)
        if last_was_progress:
            sys.stdout.write("\n")
        process.wait()
    except KeyboardInterrupt:
        process.terminate()
        process.wait()
        console.print("\n[yellow]Interrupted by user[/yellow]")
        return 130

    exit_code = process.returncode
    if exit_code != 0:
        console.print(f"\n[yellow]Command:[/yellow] [cyan]{' '.join(cmd)}[/cyan]")
        if cwd:
            console.print(f"[yellow]Working directory:[/yellow] [cyan]{cwd}[/cyan]")
    return exit_code


def compile(fqbn: str, sketch_path: str = ".") -> int:
    """Compile sketch for given FQBN."""
    console.print(f"[cyan]Compiling with FQBN: {fqbn}[/cyan]")
    return run(["compile", "--fqbn", fqbn, "."], cwd=Path(sketch_path))


def with_upload_speed(fqbn: str, upload_speed: int) -> str:
    """Add the UploadSpeed board option for ESP cores; other cores (e.g. AVR) have no such option."""
    if not fqbn.startswith(ESP_CORE_PREFIXES):
        return fqbn
    separator = "," if fqbn.count(":") >= 3 else ":"
    return f"{fqbn}{separator}UploadSpeed={upload_speed}"


def upload(fqbn: str, port: str, upload_speed: int, sketch_path: str = ".") -> int:
    """Upload sketch to port, at the given speed where the board supports it."""
    upload_fqbn = with_upload_speed(fqbn, upload_speed)
    speed_note = f" at {upload_speed} baud" if upload_fqbn != fqbn else ""
    console.print(f"[cyan]Uploading to {port}{speed_note}[/cyan]")
    return run(["upload", "--fqbn", upload_fqbn, "--port", port, "."], cwd=Path(sketch_path))


def monitor(port: str, baudrate: int) -> int:
    """Open serial monitor on port at baudrate."""
    check_arduino_cli()
    console.print(f"[cyan]Monitoring {port} at {baudrate} baud[/cyan]")
    console.print("[yellow]Press Ctrl+C to exit monitor[/yellow]\n")
    cmd = ["arduino-cli", "monitor", "--port", port, "--config", f"baudrate={baudrate}"]
    try:
        result = subprocess.run(cmd)
        return result.returncode
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        return 130
