from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlmodel import select

from ..database import SessionDep
from ..utils import PaginationQuery, paginate
from .dto import HighlightedPhraseCreate, HighlightedPhrasePatch, HighlightedPhraseUpdate
from .model import HighlightedPhrase


class HighlightedPhraseService:
    def __init__(self, session):
        self.session = session

    def all(
        self, pagination: PaginationQuery | None = None
    ) -> Sequence[HighlightedPhrase | type[HighlightedPhrase]]:
        query = select(HighlightedPhrase)

        if pagination is not None:
            query = paginate(query, pagination)

        all = self.session.exec(query).all()
        return all

    def create(
        self, create: HighlightedPhraseCreate
    ) -> HighlightedPhrase | type[HighlightedPhrase]:
        phrase = HighlightedPhrase.model_validate(create.model_dump())
        self.session.add(phrase)
        self.session.commit()
        self.session.refresh(phrase)
        return phrase

    def get(self, phrase_id: int) -> HighlightedPhrase | type[HighlightedPhrase]:
        phrase = self.session.get(HighlightedPhrase, phrase_id)
        return phrase

    def update(
        self, phrase: HighlightedPhrase | type[HighlightedPhrase], update: HighlightedPhraseUpdate
    ) -> HighlightedPhrase | type[HighlightedPhrase]:
        self._patch_phrase(phrase, update)
        self.session.commit()
        self.session.refresh(phrase)
        return phrase

    def patch(
        self, phrase: HighlightedPhrase | type[HighlightedPhrase], patch: HighlightedPhrasePatch
    ) -> HighlightedPhrase | type[HighlightedPhrase]:
        self._patch_phrase(phrase, patch)
        self.session.commit()
        self.session.refresh(phrase)
        return phrase

    def delete(self, phrase: HighlightedPhrase | type[HighlightedPhrase]):
        self.session.delete(phrase)
        self.session.commit()

    def _patch_phrase(
        self,
        phrase: HighlightedPhrase | type[HighlightedPhrase],
        patch: HighlightedPhraseUpdate | HighlightedPhrasePatch,
    ) -> HighlightedPhrase | type[HighlightedPhrase]:
        updates = patch.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(phrase, key, value)

        self.session.add(phrase)


def get_highlighted_phrase_service(session: SessionDep):
    return HighlightedPhraseService(session)


HighlightedPhraseServiceDep = Annotated[
    HighlightedPhraseService, Depends(get_highlighted_phrase_service)
]
