from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_NAME = "Trakt API"
DESCRIPTION = "The API for the Trakt RSS feed aggregator."
VERSION = "0.1.0"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_environment: str = Field(default="production")
    clerk_secret_key: str = Field()
    clerk_authorized_parties: str = Field()

    @computed_field
    @property
    def clerk_authorized_parties_list(self) -> list[str]:
        return self.clerk_authorized_parties.split(",")

    @computed_field
    @property
    def dev_mode(self) -> bool:
        return self.app_environment == "development"


@lru_cache
def get_settings():
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
