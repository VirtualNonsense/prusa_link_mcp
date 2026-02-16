import httpx
import pytest
import pytest_asyncio

from prusa_mcp.io import get_files_list, get_storage_list, get_print_files_list
from prusa_mcp.printer import start_print_job, get_printer_status
from prusa_mcp.settings import PrinterConfig


@pytest_asyncio.fixture(autouse=True)
async def check_printer(settings: PrinterConfig) -> None:
    try:
        await get_printer_status(settings)
    except Exception as err:
        pytest.skip(f"The test was skipped due to {err}. "
                    f"These tests are integration tests. Please check the configuration as well as your connection to the printer.")


@pytest.mark.asyncio
async def test_start_print_job(settings: PrinterConfig) -> None:
    t = (await get_print_files_list(settings)).files
    assert len(t) > 0 and t[0].display_name is not None
    await start_print_job(t[0].display_name, settings)


@pytest.mark.asyncio
async def test_fetch_files(settings: PrinterConfig) -> None:
    header = settings.header()
    storages = await get_storage_list(url=settings.base_url(), header=header)
    files = await get_files_list(url=settings.base_url(), header=header, storage_list=storages)
    for file in files.files:
        async with httpx.AsyncClient() as client:
            assert file.file_path is not None
            response = await client.get(file.file_path, headers=header)
            response.raise_for_status()
