from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies.auth import get_current_user, require_any_role, require_role
from src.models.user import User

router = APIRouter()


@router.get("/user", response_model=dict)
async def get_user_data(
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    return {
        "message": "This is user-specific data",
        "user_id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
    }


@router.get("/admin", response_model=dict)
async def get_admin_data(
    current_user: Annotated[User, Depends(require_role("admin"))],
) -> dict:
    return {
        "message": "This is admin-only data",
        "user_id": current_user.id,
        "email": current_user.email,
    }


@router.get("/moderator", response_model=dict)
async def get_moderator_data(
    current_user: Annotated[User, Depends(require_any_role("moderator", "admin"))],
) -> dict:
    return {
        "message": "This is moderator data",
        "user_id": current_user.id,
        "email": current_user.email,
    }
