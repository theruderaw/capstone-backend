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
        "table":"user_personal"
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
        "table":"user_personal",
        "where":[["user_id","=",user_id]]
    }
    return delete(db_payload)
