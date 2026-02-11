# routers/info.py
from fastapi import APIRouter, HTTPException
from auth import get_status, require_perm
from services.info_service import get_user_info

router = APIRouter(prefix="/info", tags=["Info"])

@router.get("/user", summary="Get personal info for a user")
def user_info(user_id: int):
    status = get_status(user_id)
    require_perm(status, 1)

    try:
        info = get_user_info(user_id)
        return {"status": "OK", "data": info}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))