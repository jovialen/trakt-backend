from sqlmodel import Field, SQLModel

HEX_REGEX = r"^#(?:[0-9a-fA-F]{3}){1,2}$"


class HighlightedPhraseBase(SQLModel):
    phrase: str = Field(min_length=1, max_length=100, unique=True)
    color: str = Field(schema_extra={"pattern": HEX_REGEX})


class HighlightedPhrase(HighlightedPhraseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
