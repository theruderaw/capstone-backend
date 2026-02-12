import bcrypt
from db import get_connection
from crud import create,read,update
from fastapi import HTTPException

def add_password(user_id, password):
    """
    Adds a password for a given user in the auth table.
    Check if an auth record already exists.
    """
    remove(user_id)
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # Prepare payload
    payload = {
        "table": "auth",
        "data": {
            "user_id": user_id,
            "password_hash": hashed_password,
            "active": True
        }
    }

    create(payload)

def remove(user_id):
    table = "auth"
    payload = {
        "table":table,
        "data":{
            "active":False
        },
        "where":[["user_id","=",user_id]]
    }
    update(payload)
    


import bcrypt

def check_password(user_identifier, entered_password):
    """
    Returns (True, user_id) if password matches
    Returns (False, None) otherwise
    user_identifier can be user_id (int) or email (str)
    """
    conn = get_connection()
    cursor = conn.cursor()

    if isinstance(user_identifier, int):
        cursor.execute("""
            SELECT a.password_hash, a.user_id
            FROM auth a
            WHERE a.user_id = %s
              AND COALESCE(a.active, TRUE) = TRUE
        """, (user_identifier,))
    else:
        cursor.execute("""
            SELECT a.password_hash, u.user_id
            FROM auth a
            JOIN user_personal u ON u.user_id = a.user_id
            WHERE u.email = %s
              AND COALESCE(a.active, TRUE) = TRUE
        """, (user_identifier,))

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return False, None

    password_hash, user_id = row

    is_valid = bcrypt.checkpw(
        entered_password.encode("utf-8"),
        password_hash.encode("utf-8")
    )

    return is_valid, user_id

def get_perms(status_id):
    rows = ["p.permission_id as id","p.code as perm","p.description"]
    table = "status_permission sp JOIN permission p ON p.permission_id = sp.permission_id"
    where = [["sp.status_id","=",status_id]]
    payload = {
        "rows":rows,
        "table":table,
        "where":where
    }
    return read(payload)

def require_perm(status_id,perm_needed):
    rows = ["permission_id"]
    table = "status_permission"
    where = [["status_id","=",status_id]]
    payload = {
        "rows":rows,
        "table":table,
        "where":where
    }
    data = read(payload)
    print([i["permission_id"] for i in data],perm_needed    )
    if perm_needed not in [i["permission_id"] for i in data]:
        raise HTTPException(403)
    return True

def get_status(user_id):
    query = f"SELECT status_id FROM user_personal where user_id = {user_id}"
    data = read(payload = {
        "query":query
    })
    if not data:
        raise HTTPException(403)
    status = data[0]["status_id"]
    return status



if __name__ == "__main__":
    add_password(6,"abcdefgh")