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
    Returns True if the entered_password matches the stored hash for the user.
    user_identifier can be user_id (int) or email (str)
    Returns False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Determine if user_identifier is numeric (user_id) or string (email)
    if isinstance(user_identifier, int):
        # Lookup by user_id
        cursor.execute("""
            SELECT a.password_hash
            FROM auth a
            WHERE a.user_id = %s AND a.active = True
        """, (user_identifier,))
    else:
        # Lookup by email -> join with user_personal
        cursor.execute("""
            SELECT a.password_hash,u.user_id
            FROM auth a
            JOIN user_personal u ON u.user_id = a.user_id
            WHERE u.email = %s AND a.active = True
        """, (user_identifier,))

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        # No matching auth record found
        return False

    password_hash = row[0]
    # Compare entered password with hash
    return [bcrypt.checkpw(entered_password.encode(), password_hash.encode()),row[1]]

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