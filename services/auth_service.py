from auth import check_password, get_perms, add_password
from crud import read

def authenticate_user(user_id_or_name: str, password: str):

    valid, user_id = check_password(user_id_or_name, password)
    return valid, user_id


def get_user_session(user_id: int):
    rows = ["us.user_id", "us.name", "st.status_id", "st.name as status_name"]
    table = "user_personal us JOIN status st ON st.status_id = us.status_id"
    where = [["us.user_id", "=", user_id]]

    payload = {
        "table": table,
        "rows": rows,
        "where": where
    }

    data = read(payload)
    if not data:
        return None

    user_info = data[0]
    perms = get_perms(user_info["status_id"])

    return {
        "user_id": user_info["user_id"],
        "name": user_info["name"],
        "status_id": user_info["status_id"],
        "status_name": user_info["status_name"],
        "perms": perms
    }


def reset_password(user_id: int, old_password: str, new_password: str) -> bool:
    """
    Reset a user's password.
    Returns True if successful, raises exception if fails.
    """
    if not check_password(user_id, old_password):
        return False

    add_password(user_id, new_password)
    return True