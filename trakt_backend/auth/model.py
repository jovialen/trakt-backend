from datetime import UTC, datetime

from pydantic import BaseModel, Field, computed_field, field_validator
from pydantic_settings import SettingsConfigDict


class UserToken(BaseModel):
    model_config = SettingsConfigDict(frozen=True)

    authorized_party: str = Field(alias="azp")
    expires_at: datetime = Field(alias="exp")
    issued_at: datetime = Field(alias="iat")
    issuer: str = Field(alias="iss")
    not_valid_before: datetime = Field(alias="nbf")
    session_id: str = Field(alias="sid")
    sub: str = Field(alias="sub")
    version: int = Field(alias="v")
    features: tuple[int, ...] = Field(alias="fva")
    session_status: str = Field(alias="sts")

    @field_validator("expires_at", "issued_at", "not_valid_before", mode="before")
    @classmethod
    def parse_timestamp(cls, value: int) -> datetime:
        return datetime.fromtimestamp(value, UTC)

    @computed_field
    @property
    def user_id(self) -> str:
        return self.sub

    @computed_field
    @property
    def is_valid(self) -> bool:
        now = datetime.now(UTC)
        return self.not_valid_before <= now <= self.expires_at
