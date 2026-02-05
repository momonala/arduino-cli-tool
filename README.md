# arduino-cli-tool

Simplified CLI wrapper for `arduino-cli` with automatic board detection and streamlined workflow.

## Installation

1. Install dependencies:
```bash
uv sync
```

2. Set up alias (optional). Use the project script name so it works from any directory (even inside other uv projects); `python -m src.arduino` can fail when cwd is another project because Python resolves `src` from the current directory:
```bash
alias arduino='uv run --project ~/code/projects/arduino-cli-tool arduino-cli-tool'
```

## Quick Start

```bash
# Compile only
arduino compile

# Upload (auto-detects USB board)
arduino upload

# Monitor serial port
arduino monitor

# Run all three in sequence
arduino run

# Show connected USB boards
arduino show boards

# Show installed libraries
arduino show libraries
```

## Configuration

Edit `pyproject.toml` under `[tool.arduino]`:

```toml
[tool.arduino]
fqbn = "esp32:esp32:esp32"
upload_speed = 115200
baudrate = 115200
sketch_path = "."
```

All values can be overridden via CLI flags.

## Commands

### Build & Upload

- `arduino compile [--fqbn FQBN] [--path PATH]` - Compile sketch
- `arduino upload [--fqbn FQBN] [--port PORT] [--speed SPEED] [--path PATH]` - Upload to board
- `arduino monitor [--port PORT] [--baudrate BAUDRATE]` - Open serial monitor
- `arduino run [--fqbn FQBN] [--port PORT] [--speed SPEED] [--baudrate BAUDRATE] [--path PATH]` - Compile, upload, then monitor

### Information

- `arduino show boards` - Show connected USB boards
- `arduino show libraries` - Show installed libraries
- `arduino show cores` - Show installed cores/platforms
- `arduino show config` - Show current tool configuration
- `arduino version` - Show arduino-cli version

## Examples

```bash
# Compile with custom FQBN
arduino compile --fqbn esp32:esp32:esp32

# Upload to specific port
arduino upload --port /dev/cu.usbserial-110 --speed 921600

# Run with all custom options
arduino run --fqbn esp32:esp32:esp32 --port /dev/cu.usbserial-110 --speed 921600 --baudrate 115200
```

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management
- `arduino-cli` installed and in PATH

## Project Structure

```
src/
├── arduino.py          # Main CLI entry point
├── board.py            # Board detection logic
├── cli.py              # arduino-cli execution with streaming
├── info.py             # Info display commands
└── arduino_config.py   # Configuration management
```
