"""MCP server for Prusa 3D printers (PrusaLink API)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

from prusa_mcp.io import get_print_files_list, get_job_status, PrinterStatus
from prusa_mcp.printer import start_print_job,  get_printer_status, stop_print_job, pause_print_job, \
    resume_print_job
from prusa_mcp.settings import get_printer_settings

mcp = FastMCP("Prusa Printer")

# ── Helpers ──────────────────────────────────────────────────────────────────
settings = get_printer_settings()


# ── Tools ────────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_status() -> dict[str, Any]:
    """Get the current printer status."""
    return await get_printer_status(settings)


@mcp.tool()
async def get_gcode_files() -> dict[str, Any]:
    """List files on the printer for a given storage and path.

    Use get_storage_list() first to discover available storages.
    """

    return (await get_print_files_list(settings)).model_dump()


@mcp.tool()
async def upload_file(
        file_path: str,
        filename: str,
        storage: str = "usb",
        print_after_upload: bool = False,
) -> dict[str, Any]:
    """Upload a file to the printer via PUT. Optionally start printing immediately.

    Args:
        file_path: Local path to the file to upload.
        filename: Target filename on the printer.
        storage: Target storage, e.g. 'usb' or 'local'.
        print_after_upload: Whether to start printing after upload.
    """
    url = f"{settings.base_url()}/files/{storage}/{filename.strip('/')}"
    path = Path(file_path)

    put_headers = {
        **settings.header(),
        "Content-Type": "application/octet-stream",
        "Print-After-Upload": "1" if print_after_upload else "0",
    }

    async with httpx.AsyncClient() as client:
        with path.open("rb") as fh:
            response = await client.put(
                url,
                content=fh.read(),
                headers=put_headers,
            )
        response.raise_for_status()

        # Some firmware versions return empty body on 201/204
        if response.status_code in (201, 204) or not response.content:
            return {"success": True, "status_code": response.status_code}

        result: dict[str, Any] = response.json()
        return result


@mcp.tool()
async def start_job(filename: str) -> dict[str, Any]:
    """Start printing a file that is already on the printer."""

    return await start_print_job(filename, settings)


@mcp.tool()
async def cancel_job() -> dict[str, Any]:
    """Cancel the current print job."""
    return await stop_print_job(settings)


@mcp.tool()
async def resume_job() -> dict[str, Any]:
    """resumes the current print job."""
    return await resume_print_job(settings)


@mcp.tool()
async def pause_job() -> dict[str, Any]:
    """pause the current print job."""
    return await pause_print_job(settings)


@mcp.tool()
async def job_status() -> PrinterStatus:
    """The status of the current job."""
    return await get_job_status(settings)


if __name__ == "__main__":
    mcp.run()
