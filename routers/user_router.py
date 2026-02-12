from fastapi import APIRouter,HTTPException,Query
from services.user_service import delete_user,create_user,get_user,get_all_user,update_user
from services.auth_service import add_password
from auth import get_status,require_perm
from schemas import UserCreate,EditUser,UserAction

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@router.post("/add")
def create_new_user(user_id:int,payload:UserCreate):
    status = get_status(user_id=user_id)
    require_perm(status,9)
    try:
        data = create_user(payload.user_personal)
        add_password(data[0]["user_id"],payload.auth.password)
        return {"status":"OK","user_id":data[0]["user_id"]}
    except Exception as e:
       raise HTTPException(status_code=500,detail=f"{e}")

@router.get("/{user_id}")
def view_self_data(user_id:int):
    status = get_status(user_id=user_id)
    require_perm(status,7)
    try:
        data = get_user(user_id)
        print(data)
        if not data:
            raise HTTPException(status_code=404,detail="User Not Found")
        return {
            "status":"OK",
            "data":data
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")
    
@router.get("/all/{user_id}")
def view_all_user_data(user_id:int):
    status = get_status(user_id=user_id)
    require_perm(status,8)
    try:
        data = get_all_user(user_id)
        if not data:
            raise HTTPException(status_code=404,detail="User Not Found")
        return {
            "status":"OK",
            "data":data
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")
    
@router.patch("/edit/{user_id}")
def edit_user_data(user_id:int, payload: EditUser):
    status = get_status(payload.user_action.user_id)
    require_perm(status,10)
    try:
        data = update_user(payload.user_personal,user_id)
        if not data:
            raise HTTPException(status_code=404,detail="User Not Found")
        return {
            "status":"OK",
            "data":data
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")
    
@router.patch("/delete/{user_id}")
def delete_user_data(user_id:int, payload: UserAction):
    status = get_status(payload.user_id)
    require_perm(status,10)
    try:
        data = delete_user(user_id)
        if not data:
            raise HTTPException(status_code=404,detail="User Not Found")
        return {
            "status":"OK",
            "data":data
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")