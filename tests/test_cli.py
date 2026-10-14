import pytest

from src.cli import with_upload_speed


@pytest.mark.parametrize(
    "fqbn,expected",
    [
        ("esp32:esp32:esp32", "esp32:esp32:esp32:UploadSpeed=921600"),
        ("esp32:esp32:esp32:PSRAM=enabled", "esp32:esp32:esp32:PSRAM=enabled,UploadSpeed=921600"),
        ("arduino:avr:pro:cpu=16MHzatmega328", "arduino:avr:pro:cpu=16MHzatmega328"),
        ("arduino:avr:nano", "arduino:avr:nano"),
    ],
)
def test_with_upload_speed(fqbn: str, expected: str):
    assert with_upload_speed(fqbn, 921600) == expected
