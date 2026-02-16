from crud import create,read,update,delete

def add_helmet(user_id:int,rfid_tag:int):
    db_payload = {
        "table":"helmet",
        "data":{
            "user_id":user_id,
            "rfid_tag":rfid_tag
        }
    }
    return create(db_payload)

def activate_helmet(helmet_id:int):
    db_payload = {
        "table":"helmet",
        "data":{
            "active":True
        },
        "where":[["helmet_id","=",helmet_id]]
    }
    return update(db_payload)


def get_helmet_by_userId(user_id):
    db_payload = {
        "rows":["helmet_id"],
        "table":"helmet",
        "where":[["user_id","=",user_id]]
    }
    return read(db_payload)

def flip_state(user_id):
    db_payload = {
        "table":"helmet",
        "data":{
            "online":"not online"
        },
        "where":[["user_id","=",user_id]]
    }
    return update(user_id)
