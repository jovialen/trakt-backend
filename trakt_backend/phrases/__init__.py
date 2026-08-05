from .controller import router
from .dto import HighlightedPhraseCreate, HighlightedPhrasePatch, HighlightedPhraseUpdate
from .model import HighlightedPhrase
from .service import (  # noqa: E501
    HighlightedPhraseService,
    HighlightedPhraseServiceDep,
    get_highlighted_phrase_service,
)
