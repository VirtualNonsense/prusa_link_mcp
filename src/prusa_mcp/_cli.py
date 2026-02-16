import subprocess
import sys
from logging import getLogger
from pathlib import Path
from socketserver import ThreadingTCPServer
from typing import Optional
import logging

import click

from prusa_mcp.proxy import *
from prusa_mcp.settings import get_mcpo_settings

LOG = getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

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
@click.option("--target_host", type=str, help="Hostname or IP address of the actual mcp server")
@click.option("--target_port", type=int, help="Port number")
@click.option("--listen_host", type=str, help="Hostname or IP address of the open webui bound host")
@click.option("--listen_port", type=int, help="Port number")
@click.option("--buffer_size", type=int, help="Size of the buffer")
@click.option("--no_tcp_nodelay", type=int, help="Disable TCP_NODELAY")
def proxy(target_host: Optional[str] = None,
          target_port: Optional[int] = None,
          listen_host: Optional[int] = None,
          listen_port: Optional[int] = None,
          buffer_size: Optional[int] = None,
          no_tcp_nodelay: Optional[bool] = None) -> None:
    settings = get_mcpo_settings()
    target_host = target_host or settings.mcpo_ip
    target_port = target_port or settings.mcpo_port

    buffer_size = buffer_size or 64 * 1024
    listen_host = listen_host or "0.0.0.0"  # type: ignore[assignment]
    listen_port = listen_port or 5000

    assert target_host is not None
    assert target_port is not None
    assert listen_host is not None
    assert listen_port is not None


    target = Endpoint(target_host, target_port)
    handler_cls = make_handler_class(
        target=target,
        buffer_size=buffer_size,
        tcp_nodelay=not no_tcp_nodelay,
    )
    LOG.info("proxy started.")

    with ThreadingTCPServer((listen_host, listen_port), handler_cls) as srv:
        LOG.info(
            "Listening on %s:%d -> forwarding to %s:%d",
            listen_host,
            listen_port,
            target_host,
            target_port,
        )
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            LOG.info("Shutting down.")


if __name__ == '__main__':
    proxy()
