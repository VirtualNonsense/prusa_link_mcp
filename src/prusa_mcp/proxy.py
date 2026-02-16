#!/usr/bin/env python3
from __future__ import annotations

import logging
import select
import socket
import socketserver
from dataclasses import dataclass
from typing import Final, Optional, Type

LOG = logging.getLogger("tcp_proxy_threaded")


@dataclass(frozen=True, slots=True)
class Endpoint:
    host: str
    port: int


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads: bool = True
    allow_reuse_address: bool = True


class ProxyHandler(socketserver.BaseRequestHandler):
    """
    A single client connection handler. Connects to the configured target and
    forwards bytes in both directions until either side closes.
    """

    def __init__(
            self,
            request: socket.socket,
            client_address: tuple[str, int],
            server: socketserver.BaseServer,
            *,
            target: Endpoint,
            buffer_size: int,
            tcp_nodelay: bool,
    ) -> None:
        self._target: Endpoint = target
        self._buffer_size: int = buffer_size
        self._tcp_nodelay: bool = tcp_nodelay
        super().__init__(request, client_address, server)

    def handle(self) -> None:
        client_sock: socket.socket = self.request

        if self._tcp_nodelay:
            self._set_tcp_nodelay(client_sock)

        try:
            with socket.create_connection((self._target.host, self._target.port)) as upstream:
                if self._tcp_nodelay:
                    self._set_tcp_nodelay(upstream)

                self._bidirectional_copy(client_sock, upstream)
        except Exception:
            LOG.exception(
                "Connection handling failed for client=%s target=%s:%d",
                self.client_address,
                self._target.host,
                self._target.port,
            )

    def _bidirectional_copy(self, a: socket.socket, b: socket.socket) -> None:
        sockets: Final[list[socket.socket]] = [a, b]

        while True:
            readable, _, _ = select.select(sockets, [], [])
            if a in readable:
                if not self._recv_and_send(src=a, dst=b):
                    return
            if b in readable:
                if not self._recv_and_send(src=b, dst=a):
                    return

    def _recv_and_send(self, *, src: socket.socket, dst: socket.socket) -> bool:
        data = src.recv(self._buffer_size)
        if not data:
            return False
        dst.sendall(data)
        return True

    @staticmethod
    def _set_tcp_nodelay(sock: socket.socket) -> None:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)


def make_handler_class(
        *,
        target: Endpoint,
        buffer_size: int,
        tcp_nodelay: bool,
) -> Type[socketserver.BaseRequestHandler]:
    """
    Returns a BaseRequestHandler class bound to a specific configuration.
    This avoids untyped server attribute injection and stays mypy-friendly.
    """

    class BoundProxyHandler(ProxyHandler):
        def __init__(
                self,
                request: socket.socket,
                client_address: tuple[str, int],
                server: socketserver.BaseServer,
        ) -> None:
            super().__init__(
                request,
                client_address,
                server,
                target=target,
                buffer_size=buffer_size,
                tcp_nodelay=tcp_nodelay,
            )

    return BoundProxyHandler



def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose > 0 else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    target = Endpoint(args.target_host, args.target_port)
    handler_cls = make_handler_class(
        target=target,
        buffer_size=args.buffer_size,
        tcp_nodelay=not args.no_tcp_nodelay,
    )

    with ThreadingTCPServer((args.listen_host, args.listen_port), handler_cls) as srv:
        LOG.info(
            "Listening on %s:%d -> forwarding to %s:%d",
            args.listen_host,
            args.listen_port,
            target.host,
            target.port,
        )
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            LOG.info("Shutting down.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
