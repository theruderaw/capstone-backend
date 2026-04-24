from crud import create,update,read
import secrets
from schemas import HelmetAssign

def create_helmet():
    db_payload = {
        "data":{
            "rfid_tag":secrets.token_hex(16)
        },
        "table":"helmet"
    }
    return create(db_payload)

def assign_helmet(payload:HelmetAssign):
    db_payload = {
        "data":{
            "helmet_id":payload.helmet_id
        },
        "table":"user_personal",
        "where":[["user_id","=",payload.user_id]]
    }
    return update(db_payload)

def get_user_id(helmet_id):
    db_payload = {
        "rows":["user_id"],
        "table":"user_personal",
        "where":[["helmet_id","=",helmet_id]]
    }
    return read(db_payload)