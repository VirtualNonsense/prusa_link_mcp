from __future__ import annotations

from enum import Enum
from typing import Optional, Any, List

import httpx
from pydantic import BaseModel, Field

__all__ = [

    "StorageList",
    "get_print_files_list",
    "get_job_status",
    "PrinterStatus",

]

from prusa_mcp.settings import PrinterConfig


class EntryType(str, Enum):
    FOLDER = "FOLDER"
    FILE = "FILE"
    PRINT_FILE = "PRINT_FILE"


class FolderEntry(BaseModel):
    name: str = Field(..., description="Nme of the object")
    type: EntryType = Field(..., description="Type of the object")
    ro: bool = Field(description="Read-only flag")
    m_timestamp: Optional[int] = Field(None, description="Timestamp of the object")
    display_name: Optional[str] = Field(None, description="Display name of the object")
    children: Optional[list[FolderEntry]] = Field(None,
                                                  description="Children of the object. Will be none in case it is a file")
    file_path: Optional[str] = Field(None, description="The full file path of the object")


FolderEntry.model_rebuild()


class StorageContent(BaseModel):
    files: list[FolderEntry]


class StorageItem(BaseModel):
    path: str
    name: str
    type: str
    read_only: bool
    available: bool


class StorageList(BaseModel):
    storage_list: list[StorageItem]


class FileRefs(BaseModel):
    icon: str
    thumbnail: str
    download: str


class FileInfo(BaseModel):
    refs: FileRefs
    name: str
    display_name: str
    path: str
    size: int
    m_timestamp: int


class PrinterStatus(BaseModel):
    id: int
    state: str
    progress: float
    time_remaining: int
    time_printing: int
    file: FileInfo


async def get_storage_list(url: str, header: dict[str, Any]) -> StorageList:
    """List available storage locations on the printer (e.g. 'usb', 'local')."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{url}/storage", headers=header)
        response.raise_for_status()
        result: dict[str, Any] = response.json()
        return StorageList.model_validate(result)


async def recursive_get_files(header: dict[str, Any], path: str, files: list[FolderEntry]) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{path}", headers=header)
        response.raise_for_status()
        result: dict[str, Any] = response.json()
        entry = FolderEntry.model_validate(result)
        match entry.type:
            case EntryType.FOLDER:
                for child in (entry.children or []):
                    await recursive_get_files(header, f"{path}/{child.display_name}", files)
                return None
            case EntryType.FILE:
                pass
            case EntryType.PRINT_FILE:
                if entry.display_name is not None:
                    entry.file_path = path
                    files.append(entry)
                return None


async def get_files_list(url: str, header: dict[str, Any], storage_list: StorageList) -> StorageContent:
    files: List[FolderEntry] = []
    for storage in storage_list.storage_list:
        path = storage.path.replace("/", "")
        await recursive_get_files(header, f"{url}/files/{path}", files)
    return StorageContent(files=files)


async def get_print_files_list(settings: PrinterConfig) -> StorageContent:
    storages = await get_storage_list(url=settings.base_url(), header=settings.header())
    return await get_files_list(url=settings.base_url(), header=settings.header(), storage_list=storages)


async def get_job_status(settings: PrinterConfig) -> PrinterStatus:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.base_url()}/job", headers=settings.header())
        response.raise_for_status()

        status = PrinterStatus.model_validate(response.json())
        return status
