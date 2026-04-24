from crud import read, update, create, delete
from auth import add_password
from schemas import UserPersonal,Auth

def create_user(user_personal_data:UserPersonal):
    db_payload = {
        "table":"user_personal",
        "data":{
            "aadhar_no":user_personal_data.aadhar_no,
            "dob":user_personal_data.dob,
            "name":user_personal_data.name,
            "gender":user_personal_data.gender,
            "father_name":user_personal_data.father_name,
            "status_id":user_personal_data.status_id,
            "address":user_personal_data.address,
            "active":user_personal_data.active,
            "email":user_personal_data.email
        }
    }
    return create(db_payload)

def get_user(user_id:int):
    db_payload = {
        "table":"user_personal",
        "where":[["user_id","=",user_id]]
    }
    return read(db_payload)

def get_all_user(user_id:int):
    db_payload = {
        "rows":["up.*","s.name as status_name"],
        "table":"user_personal up JOIN status s ON s.status_id = up.status_id",
        "where":[["active","=",True]],
        "order_by":[["user_id","ASC"]]
    }
    return read(db_payload)

def update_user(user_personal_data:UserPersonal,user_id:int):
    db_payload = {
        "table":"user_personal",
        "data": user_personal_data.model_dump(),
        "where":[["user_id","=",user_id]]
    }
    return update(db_payload)

def delete_user(user_id:int):
    db_payload = {
        "data":{"active":False},
        "table":"user_personal",
        "where":[["user_id","=",user_id]]
    }
    return update(db_payload)


def get_supervisors(status_id:int):
    db_payload = {
        "rows":["user_id","name"],
        "table":"user_personal",
        "where":[["status_id","=",2 if status_id != 2 else 3]]
    }
    return read(db_payload)
def get_supervisor_hierarchy(user_id: int):
    # Get level 1 supervisor
    res1 = read({
        "table": "user_personal",
        "rows": ["supervisor"],
        "where": [["user_id", "=", user_id]]
    })
    
    if not res1 or not res1[0]["supervisor"]:
        return []
    
    sup1_id = res1[0]["supervisor"]
    sup1_data = read({"table": "user_personal", "rows": ["name"], "where": [["user_id", "=", sup1_id]]})
    sup1_name = sup1_data[0]["name"] if sup1_data else "Unknown"
    
    hierarchy = [{"user_id": sup1_id, "name": sup1_name, "level": 1}]
    
    # Get level 2 supervisor
    res2 = read({
        "table": "user_personal",
        "rows": ["supervisor"],
        "where": [["user_id", "=", sup1_id]]
    })
    
    if res2 and res2[0]["supervisor"]:
        sup2_id = res2[0]["supervisor"]
        sup2_data = read({"table": "user_personal", "rows": ["name"], "where": [["user_id", "=", sup2_id]]})
        sup2_name = sup2_data[0]["name"] if sup2_data else "Unknown"
        hierarchy.append({"user_id": sup2_id, "name": sup2_name, "level": 2})
        
    return hierarchy
