from fastapi import APIRouter, HTTPException
from auth import get_status, require_perm
from schemas import UserAction,UserCreate
from services.user_service import list_active_users, deactivate_user,create_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", summary="List active users")
def view_users(requester_id: int):
    status = get_status(requester_id)
    require_perm(status, 4)

    try:
        data = list_active_users()
        return {"status": "OK", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{user_id}/delete", summary="Deactivate / delete a user")
def delete_user(user_id: int, payload: UserAction):
    status = get_status(payload.user_id)
    require_perm(status, 4)

    try:
        deleted_user_id = deactivate_user(user_id)
        if not deleted_user_id:
            raise HTTPException(status_code=403, detail="Cannot delete user or already inactive")
        return {"status": "OK", "deleted": deleted_user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add", summary="Create a new user")
def create_user_route(requester_id: int, payload: UserCreate):
    status = get_status(requester_id)
    require_perm(status, 4)

    try:
        user_id = create_user(
            user_personal_data=payload.user_personal.model_dump(),
            password=payload.auth.password
        )
        return {"status": "OK", "user_added": user_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))