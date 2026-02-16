import subprocess
import sys
from pathlib import Path
from typing import Optional

import click

from prusa_mcp.settings import get_mcpo_settings


@click.group()
def prusa_mcp() -> None:
    pass

@prusa_mcp.command()
@click.option("--host", type=str, help="Hostname or IP address")
@click.option("--port", type=int, help="Port number")
def serve(host: Optional[str] = None, port: Optional[int] = None) -> None:
    current_path = Path(__file__).parent.absolute()
    app = current_path.joinpath("app.py")
    settings = get_mcpo_settings()
    python = Path(sys.executable)
    mcpo = python.parent.joinpath("mcpo")

    host = host or settings.mcpo_ip
    port = port or settings.mcpo_port
    subprocess.call([
        python,
        mcpo,
        "--host",
        host,
        "--port",
        str(port),
        "--",
        python,
        str(app)
    ])