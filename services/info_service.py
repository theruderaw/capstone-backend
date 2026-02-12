from fastapi import HTTPException
from crud import read

def get_user_info(user_id: int) -> dict:
    rows = [
        "up.name",
        "up.dob",
        "up.aadhar_no",
        "st.status_id",
        'st.name as "role"'
    ]
    table = "user_personal up JOIN status st ON st.status_id = up.status_id"
    where = [["up.user_id", "=", user_id]]

    payload = {"table": table, "rows": rows, "where": where}

    data = read(payload)
    if not data:
        raise HTTPException(status_code=404, detail="User not found")

    return data[0]

def get_supervisor(user_id:int):
    db_payload = {
        "rows":[
            "s.user_id as supervisor_id",
            "s.name as supervisor_name",
            "s.email"
        ],
        "table":"user_personal w JOIN user_personal s ON w.supervisor = s.user_id",
        "where":[["w.user_id","=",user_id]]
    }

    return read(db_payload)

def reset_working(user_id:int):
    db_payload = {
        "table":"user_personal",
        "data":{
            "working":False
        },
        "where":[["user_id","=",user_id]]
    }
    return read(db_payload)