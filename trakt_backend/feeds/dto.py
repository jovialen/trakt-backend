from .model import FeedBase


class FeedCreate(FeedBase):
    pass


class FeedUpdate(FeedBase):
    pass


class FeedPatch(FeedBase):
    name: str | None = None
    link: str | None = None


class FeedRead(FeedBase):
    id: int
    groups: list[int]
