import logging
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click

from prusa_mcp.proxy import Endpoint, make_handler_class, ThreadingTCPServer
from prusa_mcp.settings import get_mcpo_settings

LOG = logging.getLogger(__name__)


@click.group()
def prusa_mcp() -> None:
    pass


@prusa_mcp.command()
@click.option("--host", type=str, help="Hostname or IP address")
@click.option("--port", type=int, help="Port number")
def serve(host: Optional[str] = None, port: Optional[int] = None) -> None:
    current_path = Path(__file__).parent.absolute()
    app = current_path.joinpath("app.py")
    python = Path(sys.executable)
    mcpo = python.parent.joinpath("mcpo")

    settings = get_mcpo_settings()
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


@prusa_mcp.command()
@click.option("--host", type=str, help="Hostname or IP address")
@click.option("--port", type=int, help="Port number")
@click.option("--listen_port", type=int, help="Port number")
@click.option("--buffer-size", type=int, help="Size of the buffer")
@click.option("--no-tcp-nodelay", type=int, help="Disable TCP_NODELAY")
def proxy(host: Optional[str] = None,
          port: Optional[int] = None,
          listen_port: Optional[int] = None,
          buffer_size: Optional[int] = None,
          no_tcp_nodelay: Optional[bool] = None) -> None:
    listen_port = listen_port or 5000
    buffer_size = buffer_size or 64 * 1024
    no_tcp_nodelay = no_tcp_nodelay or False
    listen_host = "0.0.0.0"

    settings = get_mcpo_settings()
    target_host = host or settings.mcpo_ip
    target_port = port or settings.mcpo_port

    target = Endpoint(target_host, target_port)
    handler_cls = make_handler_class(
        target=target,
        buffer_size=buffer_size,
        tcp_nodelay=not no_tcp_nodelay,
    )

    with ThreadingTCPServer((listen_host, listen_port), handler_cls) as srv:
        LOG.info(
            "Listening on %s:%d -> forwarding to %s:%d",
            listen_host,
            listen_port,
            target.host,
            target.port,
        )
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            LOG.info("Shutting down.")


if __name__ == '__main__':
    proxy()
