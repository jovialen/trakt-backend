from datetime import UTC, datetime, timedelta

from trakt_backend.auth import UserToken


def payload(exp: datetime, nbf: datetime):
    return {
        "azp": "http://localhost:3000",
        "exp": int(exp.timestamp()),
        "iat": int((nbf - timedelta(minutes=1)).timestamp()),
        "iss": "https://clerk.example.com",
        "nbf": int(nbf.timestamp()),
        "sid": "session_123",
        "sub": "user_123",
        "v": 2,
        "fva": [1],
        "sts": "active",
    }


def test_user_token_parses_unix_timestamps():
    now = datetime.now(UTC)

    token = UserToken.model_validate(
        payload(
            exp=now + timedelta(hours=1),
            nbf=now - timedelta(minutes=1),
        ),
        by_alias=True,
    )

    assert token.expires_at.tzinfo == UTC
    assert token.issued_at.tzinfo == UTC
    assert token.not_valid_before.tzinfo == UTC


def test_user_id_maps_to_sub():
    now = datetime.now(UTC)

    token = UserToken.model_validate(
        payload(
            exp=now + timedelta(hours=1),
            nbf=now - timedelta(minutes=1),
        ),
        by_alias=True,
    )

    assert token.user_id == "user_123"


def test_is_valid_true():
    now = datetime.now(UTC)

    token = UserToken.model_validate(
        payload(
            exp=now + timedelta(hours=1),
            nbf=now - timedelta(minutes=1),
        ),
        by_alias=True,
    )

    assert token.is_valid is True


def test_is_valid_false_when_expired():
    now = datetime.now(UTC)

    token = UserToken.model_validate(
        payload(
            exp=now - timedelta(minutes=1),
            nbf=now - timedelta(hours=1),
        ),
        by_alias=True,
    )

    assert token.is_valid is False


def test_is_valid_false_before_nbf():
    now = datetime.now(UTC)

    token = UserToken.model_validate(
        payload(
            exp=now + timedelta(hours=1),
            nbf=now + timedelta(minutes=5),
        ),
        by_alias=True,
    )

    assert token.is_valid is False
