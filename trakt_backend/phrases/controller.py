from fastapi import APIRouter, HTTPException, status

from ..utils import PaginationQuery
from .dto import HighlightedPhraseCreate, HighlightedPhrasePatch, HighlightedPhraseUpdate
from .model import HighlightedPhrase
from .service import HighlightedPhraseServiceDep

router = APIRouter(
    prefix="/phrases",
    tags=["Highlighted phrases"],
)


@router.get("/new", response_model=HighlightedPhraseCreate)
def new_phrase():
    return HighlightedPhraseCreate(phrase="war", color="#ff0000")


@router.get("/", response_model=list[HighlightedPhrase])
def list_phrases(pagination: PaginationQuery, phrases: HighlightedPhraseServiceDep):
    return phrases.all(pagination)


@router.post("/", response_model=HighlightedPhrase, status_code=status.HTTP_201_CREATED)
def create_phrase(create: HighlightedPhraseCreate, phrases: HighlightedPhraseServiceDep):
    return phrases.create(create)


@router.get("/{phrase_id}", response_model=HighlightedPhrase)
def get_phrase(phrase_id: int, phrases: HighlightedPhraseServiceDep):
    phrase = phrases.get(phrase_id)

    if phrase is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phrase not found")

    return phrase


@router.put("/{phrase_id}", response_model=HighlightedPhrase)
def update_phrase(
    phrase_id: int,
    update: HighlightedPhraseUpdate,
    phrases: HighlightedPhraseServiceDep,
):
    phrase = phrases.get(phrase_id)

    if phrase is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phrase not found")

    return phrases.update(phrase, update)


@router.patch("/{phrase_id}", response_model=HighlightedPhrase)
def patch_phrase(
    phrase_id: int,
    patch: HighlightedPhrasePatch,
    phrases: HighlightedPhraseServiceDep,
):
    phrase = phrases.get(phrase_id)

    if phrase is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phrase not found")

    return phrases.patch(phrase, patch)


@router.delete("/{phrase_id}")
def delete_phrase(
    phrase_id: int,
    phrases: HighlightedPhraseServiceDep,
):
    phrase = phrases.get(phrase_id)

    if phrase is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phrase not found")

    phrases.delete(phrase)
    return {"ok": True}
