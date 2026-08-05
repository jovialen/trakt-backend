from trakt_backend.phrases import (
    HighlightedPhrase,
    HighlightedPhraseCreate,
    HighlightedPhrasePatch,
    HighlightedPhraseService,
    HighlightedPhraseUpdate,
)
from trakt_backend.utils import PaginationQuery


def test_list_phrases(
    phrase_service: HighlightedPhraseService,
    phrase_batch: list[HighlightedPhrase],
):
    phrases = phrase_service.all()

    assert len(phrases) == len(phrase_batch)


def test_list_phrases_with_pagination(
    phrase_service: HighlightedPhraseService,
    phrase_batch,
):
    phrases = phrase_service.all(PaginationQuery(limit=10, offset=0))

    assert len(phrases) == 10


def test_create_phrase(phrase_service):
    created = phrase_service.create(
        HighlightedPhraseCreate(
            phrase="war",
            color="#ff0000",
        )
    )

    assert created.id is not None
    assert created.phrase == "war"
    assert created.color == "#ff0000"


def test_get_phrase(
    phrase_service,
    war_phrase,
):
    phrase = phrase_service.get(war_phrase.id)

    assert phrase is not None
    assert phrase.id == war_phrase.id


def test_get_missing_phrase(
    phrase_service,
):
    assert phrase_service.get(999999) is None


def test_update_phrase(
    phrase_service,
    war_phrase,
):
    updated = phrase_service.update(
        war_phrase,
        HighlightedPhraseUpdate(
            phrase="peace",
            color="#ffffff",
        ),
    )

    assert updated.phrase == "peace"
    assert updated.color == "#ffffff"


def test_patch_phrase(
    phrase_service,
    war_phrase,
):
    updated = phrase_service.patch(
        war_phrase,
        HighlightedPhrasePatch(
            color="#00ff00",
        ),
    )

    assert updated.phrase == "war"
    assert updated.color == "#00ff00"


def test_delete_phrase(
    phrase_service,
    war_phrase,
):
    phrase_id = war_phrase.id

    phrase_service.delete(war_phrase)

    assert phrase_service.get(phrase_id) is None
