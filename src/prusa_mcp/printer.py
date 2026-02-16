from __future__ import annotations

from typing import Any, List

import httpx

from prusa_mcp.io import get_print_files_list
from prusa_mcp.settings import PrinterConfig


async def get_printer_status(settings: PrinterConfig) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.base_url()}/status", headers=settings.header())
        response.raise_for_status()
        result: dict[str, Any] = response.json()
        return result


async def start_print_job(
        filename_or_path: str,
        settings: PrinterConfig,
) -> dict[str, Any]:
    files = (await get_print_files_list(settings)).files

    file_paths: List[str] = [f.file_path for f in files if f.file_path is not None and (
            f.display_name == filename_or_path or f.display_name == filename_or_path)]

    if len(file_paths) == 0:
        return {"success": False, "status_code": 404, "message": "File not found"}

    if len(file_paths) > 1:
        return {
            "success": False,
            "status_code": 400,
            "message":
                "More than one file found please choose one of the following paths\n"
                "\n".join([f"-{f}" for f in file_paths])
        }
    file_path = file_paths[0]

    url = f"{file_path}"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=settings.header())
        response.raise_for_status()

        if not response.content:
            return {"success": True, "status_code": response.status_code}

        result: dict[str, Any] = response.json()
        return result


async def cancel_print_job(settings: PrinterConfig) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        payload = {"command": "cancel"}
        response = await client.post(
            f"{settings.base_url()}/job", json=payload, headers=settings.json_headers()
        )
        response.raise_for_status()
        result: dict[str, Any] = response.json()
        return result
