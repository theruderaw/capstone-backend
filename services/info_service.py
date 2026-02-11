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