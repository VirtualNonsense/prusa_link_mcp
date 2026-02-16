import pytest

from prusa_mcp.settings import get_printer_settings, PrinterConfig


@pytest.fixture
def settings() -> PrinterConfig:
    return get_printer_settings()
