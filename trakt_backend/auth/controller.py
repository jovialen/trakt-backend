from fastapi import APIRouter

from .fixtures import UserDep
from .model import UserToken

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/", response_model=UserToken)
def get_auth_token(user: UserDep):
    return user
