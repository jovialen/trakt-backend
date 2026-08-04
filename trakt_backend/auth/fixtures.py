from typing import Annotated

from clerk_backend_api import AuthenticateRequestOptions, authenticate_request_async
from fastapi import Depends, HTTPException, status
from fastapi.requests import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..settings import SettingsDep
from .model import UserToken

security = HTTPBearer(
    scheme_name="ClerkAuth",
    description="Paste a Clerk Bearer JWT here.",
)


async def get_current_user(
    request: Request,
    settings: SettingsDep,
    _: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> UserToken:
    request_state = await authenticate_request_async(
        request,
        AuthenticateRequestOptions(
            secret_key=settings.clerk_secret_key,
            authorized_parties=settings.clerk_authorized_parties_list,
        ),
    )

    if not request_state.is_signed_in:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=request_state.message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    if request_state.payload is None or request_state.payload.get("sub") is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserToken.model_validate(request_state.payload, by_alias=True)


UserDep = Annotated[UserToken, Depends(get_current_user)]
