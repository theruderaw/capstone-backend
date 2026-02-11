from fastapi import FastAPI,HTTPException,Body
from db import get_connection
from fastapi.middleware.cors import CORSMiddleware
from auth import check_password,get_perms,require_perm,get_status,add_password,remove
from typing import Dict
from crud import read,create,delete,update
import datetime
import secrets
from schemas import FinanceCreate,LoginRequest,UserAction,UserCreate,AuthReset
from psycopg2.errors import UniqueViolation
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["*"] for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/",summary="Default landing route")
def landing():
    return {"status":"OK","message":"Hello World"}

@app.post("/sessions",summary="Login / create session")
def login(payload: LoginRequest):

    user,password = payload.user,payload.password
    value,user = check_password(user,password)

    if not value:
        raise HTTPException(status_code=403)
    rows = ["us.user_id","us.name","st.status_id","st.name as status_name"]
    table = "user_personal us JOIN status st ON st.status_id = us.status_id"
    where = [["us.user_id","=",user]]

    payload = {
        "table":table,
        "rows":rows,
        "where":where
    }

    data = read(payload)
    if not data:
        raise HTTPException(404)
    data = data[0]
    user,name,statusId,statusName = data["user_id"],data["name"],data["status_id"],data["status_name"]
    
    perms = get_perms(statusId)
    
    return {
        "status":"OK",
        "user_id":user,
        "name":name,
        "statusName":statusName,
        "perms":perms
    }

@app.post("/finances/{user_id}",summary="Submit a new finance entry for a user")
def submit_payment(user_id:int,payload:FinanceCreate):
    status = get_status(user_id)
    payload = {
        "table":"user_finance",
        "data":{
            "user_id":user_id,
            "hours_worked":payload.hours,
            "penalties_observed":payload.penalties
        }
    }
    require_perm(status,1)
    try:
        data = create(payload)
        return {
            "status":"OK",
            "inserted":data
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")
    
@app.patch("/finances/{payment_id}/validate",summary="Validate a finance entry")
def validate_payment(payment_id,payload:UserAction):
    status = get_status(payload["user_id"])
    payload = {
        "table":"user_finance",
        "data":{
            "validated":True,
            "validated_by":payload.user_id
        },
        "where":[["userfinance_id","=",payment_id]]
    }
    require_perm(status,7)
    try:
        data = update(payload)
        if not data:
            raise HTTPException(404)
        return {
            "result":"OK",
            "edited":data
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")
    
@app.patch("/finances/{payment_id}/authorize",summary="Authorize / mark a finance entry as paid")
def auth_payment(payment_id,payload:UserAction):
    status = get_status(payload["user_id"])
    payload = {
        "table":"user_finance",
        "data":{
            "authorized_by":payload.user_id,
            "paid":True
        },
        "where":[["userfinance_id","=",payment_id]]
    }
    require_perm(status,5)
    try:
        data = update(payload)
        if not data:
            raise HTTPException(404)
        return {
            "result":"OK",
            "edited":data
        }
    except Exception as e:
        raise HTTPException(status_code=403,detail=f"{e}")
    
@app.get("/finances/{user_id}",summary="Get pending finances for a specific user")
def get_finances(user_id):
    rows = ["uf.userfinance_id as id","st.base_wage as base_wage","st.penalty_per_unit as penalty_per_unit","uf.user_id as user_id","up.name as name","work_date","uf.hours_worked","uf.penalties_observed","up.status_id","uf.validated","uf.paid"]
    table = "user_finance uf JOIN user_personal up ON uf.user_id = up.user_id JOIN status st ON up.status_id = st.status_id"
    where = [["uf.user_id","=",user_id],["paid","=",False]]
    payload = {
        "table":table,
        "rows":rows,
        "where":where
    }
    try:
        data = read(payload)
        if data:
            require_perm(data[0]["status_id"],1)
        return {
            "status":"OK",
            "data":data
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")
    
@app.get("/finances",summary="Get all finances with optional filters")
def get_finances_all(user_id,order:bool = True,validated:bool = False,pending:bool=False):
    status = get_status(user_id)
    
    rows = ["uf.userfinance_id as id","uf.work_date","uf.user_id","up.name","uf.hours_worked as hours","uf.penalties_observed as penalties","uf.paid","uf.validated"]
    table = "user_finance as uf JOIN user_personal as up ON up.user_id = uf.user_id"
    where = []

    if validated:
        where.append(["validated","=",True])
    if pending:
        where.append(["paid","=",False])

    order_by = [["uf.userfinance_id","ASC" if order else "DESC"]]

    payload = {
        "table":table,
        "rows":rows,
        "where":where,
        "order_by":order_by
    }

    require_perm(status,6)

    try:
        data = read(payload)
        return {
            "status": "OK",
            "data": data
        }
    except Exception as e:
        raise HTTPException(500,detail=f"{e}")
    
@app.post("/manage/{user_id}/add",summary="Create a new user")
def create_user(user_id,payload:UserCreate):
    status = get_status(user_id)
    user_personal,auth = payload.user_personal,payload.auth

    table = "user_personal"
    payload = {
        "table":table,
        "data":user_personal.model_dump()
    }
    print(user_personal.dob)
    require_perm(status,4)
    try:
        data = create(payload)
    except Exception as e:
        raise HTTPException(500,f"{e}")
    user = data[0]['user_id']
    try:
        add_password(user,auth.password)
    except Exception as e:
        raise HTTPException(403,detail=f"{e}")
    return {
        "status":"OK",
        "user_added":user
    }

@app.get("/manage/{user_id}",summary="List active users")
def view_user(user_id):
    status = get_status(user_id)

    table = "user_personal"
    where = [["active","=",True]]

    payload = {
        "table":table,
        "where":where
    }

    require_perm(status,4)

    try:
        data = read(payload)
        return {
            "status":"OK",
            "data":data
        }
    except Exception as e:
        raise HTTPException(500,detail=f"{e}")
    
@app.post("/reset/{user_id}",summary="Reset a user's password")
def reset_user(user_id:int,payload:AuthReset):
    res = check_password(user_id,payload.old_password)   
    print(res)
    if not res:
        raise HTTPException(403)
    try:
        add_password(user_id,payload.new_password)
        return {
            "status":"OK",
            "edited_for":user_id
        }
    except Exception as e:
        raise HTTPException(500,f"{e}")    

@app.patch("/manage/{user_id}/delete",summary="Deactivate / delete a user")
def delete_user(user_id,payload:UserAction):
    status = get_status(payload.user_id)

    table = "user_personal"
    data = {
        "active":False
    }
    where = [["user_id","=",user_id],["active","=",True]]
    payload = {
        "table":table,
        "data":data,
        "where":where
    }

    require_perm(status,4)

    try:
        data = update(payload)
        if not data:
            raise HTTPException(403)
        return {
            "status":"OK",
            "deleted":data[0]["user_id"]
        }
    except Exception as e:
        raise HTTPException(500,f"{e}")
    

@app.get("/info/{profile_id}/",summary="Get personal info for a user")
def get_user_basic(profile_id):
    # requester status
    status = get_status(profile_id)

    # permission 1 required
    require_perm(status, 1)

    rows = [
        "up.name",
        "up.dob",
        "up.aadhar_no",
        "st.status_id",
        'st.name as "role"'
    ]

    table = "user_personal up JOIN status st ON st.status_id = up.status_id"

    where = [["up.user_id", "=", profile_id]]

    payload = {
        "table": table,
        "rows": rows,
        "where": where
    }

    try:
        data = read(payload)

        if not data:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "status": "OK",
            "data": data[0]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

@app.post('/helmet/{user_id}')
def add_helmet(user_id):
    status = get_status(user_id)

    require_perm(status,8)
    rfid_tag = secrets.token_hex(16)
    payload = {
        "table":"helmet",
        "data":{
            "rfid_tag": rfid_tag,
            "user_id":user_id,
            "notes": f"Assigned to {user_id} on {datetime.datetime.now()}"
        }
    }

    try:
        create(payload)
        return {
            "status": "OK",
            "data":{
                "rfid_val":rfid_tag
            }
        }
    except UniqueViolation as e:
        raise HTTPException(status_code=409,detail=f"Helmet has been assigned")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")
    
@app.post("helmet/activate/{helmet_id}")
def activate_helmet(helmet_id):
    payload = {
        "table":"helmet",
        "data":{
            ""
        }
    }