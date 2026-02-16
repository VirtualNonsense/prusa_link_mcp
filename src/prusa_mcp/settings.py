from __future__ import annotations

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class PrinterConfig(BaseSettings):
    """Printer connection settings, loaded from environment variables."""

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='allow')

    printer_host: str = "192.168.0.42"
    port: int = 80
    api_key: SecretStr

    def base_url(self) -> str:
        return f"http://{self.printer_host}:{self.port}/api/v1"

    def header(self) -> dict[str, str]:
        return {"X-Api-Key": self.api_key.get_secret_value()}

    def json_headers(self) -> dict[str, str]:
        return {
            "X-Api-Key": self.api_key.get_secret_value(),
            "Content-Type": "application/json",
        }


class McpoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='allow')
    mcpo_ip: str = Field("0.0.0.0", description="host ip for the mcp server")
    mcpo_port: int = Field(5000, description="Port for the mcp server")


class ProxySettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='allow')
    target_ip: str = Field("192.167.0.100", description="host ip for the mcp server")
    listening_ip: str = Field("0.0.0.0", description="host ip for the mcp server")
    listening_port: int = Field(8000, description="Port for the mcp server")
    buffer_size: int = Field(64 * 1024, description="Buffer size in MB")
    no_tcp_nodelay: bool = Field(False, description="Whether the mcp server is running on a TCP node")


@lru_cache
def get_printer_settings() -> PrinterConfig:
    return PrinterConfig()


@lru_cache
def get_mcpo_settings() -> McpoSettings:
    return McpoSettings()


@lru_cache
def get_proxy_settings() -> ProxySettings:
    return ProxySettings()
