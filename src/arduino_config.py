import tomllib
from pathlib import Path

_CONFIG_FILE = Path(__file__).parent.parent / "pyproject.toml"


def _load() -> dict[str, str | int]:
    """Load arduino config from pyproject.toml."""
    with _CONFIG_FILE.open("rb") as f:
        data = tomllib.load(f)
    arduino = data.get("tool", {}).get("arduino", {})
    return {
        "fqbn": arduino.get("fqbn", "esp32:esp32:esp32"),
        "upload_speed": arduino.get("upload_speed", 115200),
        "baudrate": arduino.get("baudrate", 115200),
        "sketch_path": arduino.get("sketch_path", "."),
    }


def get_fqbn(override: str | None = None) -> str:
    """Return FQBN (override or config)."""
    return override or str(_load()["fqbn"])


def get_upload_speed(override: int | None = None) -> int:
    """Return upload speed in baud (override or config)."""
    return override or int(_load()["upload_speed"])


def get_baudrate(override: int | None = None) -> int:
    """Return monitor baudrate (override or config)."""
    return override or int(_load()["baudrate"])
