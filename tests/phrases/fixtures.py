import pytest
from sqlmodel import Session

from trakt_backend.phrases import (
    HighlightedPhrase,
    HighlightedPhraseService,
)

from .factory import HighlightedPhraseFactory


@pytest.fixture
def phrase_service(session: Session):
    return HighlightedPhraseService(session)


def add_phrase(phrase: HighlightedPhrase, session: Session):
    session.add(phrase)
    session.commit()
    session.refresh(phrase)
    return phrase


@pytest.fixture
def war_phrase(session: Session):
    phrase = HighlightedPhraseFactory.build(
        phrase="war",
        color="#ff0000",
    )
    return add_phrase(phrase, session)


@pytest.fixture
def ai_phrase(session: Session):
    phrase = HighlightedPhraseFactory.build(
        phrase="AI",
        color="#00ff00",
    )
    return add_phrase(phrase, session)


@pytest.fixture
def phrase_batch(session: Session):
    phrases = HighlightedPhraseFactory.batch(40)

    session.add_all(phrases)
    session.commit()

    for phrase in phrases:
        session.refresh(phrase)

    return phrases
