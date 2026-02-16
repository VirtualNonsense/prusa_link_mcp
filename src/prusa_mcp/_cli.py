import subprocess
import sys
from pathlib import Path

import click

from prusa_mcp.settings import get_mcpo_settings


@click.group()
def prusa_mcp() -> None:
    pass

@prusa_mcp.command()
def serve() -> None:
    current_path = Path(__file__).parent.absolute()
    app = current_path.joinpath("app.py")
    settings = get_mcpo_settings()
    python = Path(sys.executable)
    mcpo = python.parent.joinpath("mcpo")
    subprocess.call([
        python,
        mcpo,
        "--host",
        settings.mcpo_ip,
        "--port",
        str(settings.mcpo_port),
        "--",
        python,
        str(app)
    ])