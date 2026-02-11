from fastapi import APIRouter, HTTPException
from schemas import LoginRequest,AuthReset
from services.auth_service import authenticate_user, get_user_session, reset_password

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/login", summary="Login / create session")
def login(payload: LoginRequest):

    success, user_id = authenticate_user(payload.user, payload.password)
    if not success:
        raise HTTPException(status_code=403, detail="Invalid credentials")

    session_info = get_user_session(user_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="User not found")

    return {"status": "OK", **session_info}

@router.post("/reset/{user_id}", summary="Reset a user's password")
def reset_user(user_id: int, payload: AuthReset):
    try:
        success = reset_password(
            user_id=user_id,
            old_password=payload.old_password,
            new_password=payload.new_password
        )
        if not success:
            raise HTTPException(status_code=403, detail="Old password is incorrect")

        return {"status": "OK", "edited_for": user_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))