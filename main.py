from fastapi import FastAPI,HTTPException
from db import get_connection
from fastapi.middleware.cors import CORSMiddleware
from auth import check_password,get_perms,require_perm,get_status,add_password,remove
from typing import Dict
from crud import read,create,delete,update

app = FastAPI()


# Allow frontend origin
origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # frontend origin
    allow_credentials=True,
    allow_methods=["*"],         # GET, POST, etc
    allow_headers=["*"],         # allow all headers
)

@app.get("/")
def landing():
    return {"status":"OK","message":"Hello World"}

@app.post("/login")
def login(payload:Dict):

    user,password = payload["user"],payload["password"]
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

@app.post("/finances")
def submit_payment(payload:Dict):
    status = payload["status"]
    payload = {
        "table":"user_finance",
        "data":{
            "user_id":payload["user_id"],
            "hours_worked":payload["hours"],
            "penalties_observed":payload["penalties"]
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
    
@app.patch("/finances/{payment_id}/validate")
def validate_payment(payment_id,payload:Dict):
    status = get_status(payload["user_id"])
    payload = {
        "table":"user_finance",
        "data":{
            "validated":True,
            "validated_by":payload["user_id"]
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
    
@app.post("/finances/{payment_id}/authorize")
def auth_payment(payment_id,payload:Dict):
    status = get_status(payload["user_id"])
    payload = {
        "table":"user_finance",
        "data":{
            "authorized_by":payload["user_id"],
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
    
@app.get("/finances/me")
def get_finances(user_id):
    rows = ["uf.userfinance_id as id","uf.user_id as user_id","up.name as name","work_date","uf.hours_worked","uf.penalties_observed","up.status_id","uf.validated","uf.paid"]
    table = "user_finance uf JOIN user_personal up ON uf.user_id = up.user_id"
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
    
@app.get("/finances")
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
    
@app.post("/manage/{user_id}/add")
def create_user(user_id,payload:Dict):
    status = get_status(user_id)
    user_personal,auth = payload["user_personal"],payload["auth"]

    table = "user_personal"
    payload = {
        "table":table,
        "data":user_personal
    }
    require_perm(status,4)
    try:
        data = create(payload)
    except Exception as e:
        raise HTTPException(500,f"{e}")
    user = data[0]['user_id']
    try:
        add_password(user,auth["password"])
    except Exception as e:
        raise HTTPException(403,detail=f"{e}")
    return {
        "status":"OK",
        "user_added":user
    }

@app.get("/manage/{user_id}")
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
    
@app.post("/reset/{user_id}")
def reset_user(user_id,payload:Dict):
    res = check_password(user_id,payload["old_password"])   
    print(res)
    if not res:
        raise HTTPException(403)
    try:
        add_password(user_id,payload["new_password"])
        return {
            "status":"OK",
            "edited_for":user_id
        }
    except Exception as e:
        raise HTTPException(500,f"{e}")    

@app.post("/manage/{user_id}/delete")
def delete_user(user_id,profile_id):
    status = get_status(user_id)

    table = "user_personal"
    data = {
        "active":False
    }
    where = [["user_id","=",profile_id],["active","=",True]]
    payload = {
        "table":table,
        "data":data,
        "where":where
    }

    require_perm(user_id,4)

    try:
        remove(profile_id)
        data = update(payload)
        if not data:
            raise HTTPException(403)
        return {
            "status":"OK",
            "deleted":data[0]["user_id"]
        }
    except Exception as e:
        raise HTTPException(500,f"{e}")
    

@app.get("/info/{profile_id}/")
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
        "st.name as status_name"
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
