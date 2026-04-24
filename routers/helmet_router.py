from fastapi import APIRouter, HTTPException
from auth import get_status, require_perm
from services.helmet_service import create_helmet,assign_helmet,get_user_id
from schemas import UserAction,HelmetAssign

router = APIRouter(
    prefix="/helmet",
    tags=["Helmet"]
)

@router.get("/{helmet_id}")
def get_user(helmet_id:int):
    try:
        data = get_user_id(helmet_id)
        if not data:
            raise HTTPException(404,"Not Found")
        return {
            "status":"OK",
            "data":data[0]
        }
    except Exception as e:
        raise HTTPException(500,f"{e}")

@router.put("/add")
def add_helmet(user_id:UserAction):
    status = get_status(user_id.user_id)
    require_perm(status,21)

    try:
        data = create_helmet()
        if not data:
            raise HTTPException(404,"Not found")
        return {
            "status":"OK",
            "data":data
        }
    except Exception as e:
        raise HTTPException(500,f"{e}")

@router.patch("/assign")
def add_helmet(payload:HelmetAssign):
    status = get_status(payload.admin.user_id)
    require_perm(status,21)

    try:
        data = assign_helmet(payload)
        if not data:
            raise HTTPException(404,"Not found")
        return {
            "status":"OK",
            "data":data
        }
    except Exception as e:
        raise HTTPException(500,f"{e}")
    