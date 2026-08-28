from fastapi import APIRouter, Response, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.auth import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: CurrentUser): return current_user


@router.patch("/me", response_model=UserResponse)
def update_profile(payload: UserUpdate, current_user: CurrentUser, db: DBSession):
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(current_user, key, value)
    db.commit(); db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(current_user: CurrentUser, db: DBSession):
    db.delete(current_user); db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
