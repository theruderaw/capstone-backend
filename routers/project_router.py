from auth import get_status,require_perm
from fastapi import APIRouter,HTTPException
from services.project_service import get_project,get_members,get_project_by_user_id

router = APIRouter(
    prefix="/project",
    tags=["Project"]
)

@router.get("/{project_id}")
def read_project(project_id:int,user_id:int):
    status = get_status(user_id)
    require_perm(status,12)
    try:
        data = get_project(project_id)
        if not data:
            raise HTTPException(404,"Project Not Found")
        return {
            "status":"OK",
            "data":data if data else []
        }
    except Exception as e:
        raise HTTPException(500,f"{e}")
    
@router.get("/{project_id}/details")
def get_members_of_project(project_id:int,user_id:int):
    status = get_status(user_id)
    require_perm(status,19)
    try:
        data = get_members(project_id)
        if not data:
            raise HTTPException(404,"Resource not found. Either project doesn't exist or doesn't have any members")
        return {
            "status":"OK",
            "data":data
        }
    except Exception as e:
        raise HTTPException(500,f"{e}")
    
@router.get("/getID/{user_id}")
def get_project_id(user_id:int):
    status = get_status(user_id)
    require_perm(status,12)
    try:
        data = get_project_by_user_id(user_id=user_id)
        if not data:
            return HTTPException(404,"Not found")
        return {
            "status":"OK",
            "data":data
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")