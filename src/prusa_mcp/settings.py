from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PrinterConfig(BaseSettings):
    """Printer connection settings, loaded from environment variables."""

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='allow')

    printer_host: str = "192.168.0.42"
    port: int = 80
    api_key: str


    def base_url(self) -> str:
        return f"http://{self.printer_host}:{self.port}/api/v1"

    def header(self) -> dict[str, str]:
        return {"X-Api-Key": self.api_key}

    def json_headers(self) -> dict[str, str]:
        return {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

class McpoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='allow')
    mcpo_ip: str = Field("localhost", description="host ip for the mcp server")
    mcpo_port: int = Field(8000, description="Port for the mcp server")


@lru_cache
def get_printer_settings() -> PrinterConfig:
    return PrinterConfig()


@lru_cache
def get_mcpo_settings() -> McpoSettings:
    return McpoSettings()