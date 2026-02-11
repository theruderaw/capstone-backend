from crud import read, update, create
from auth import add_password

def list_active_users():
    payload = {
        "table": "user_personal",
        "where": [["active", "=", True]]
    }
    return read(payload)


def deactivate_user(user_id: int):
    payload = {
        "table": "user_personal",
        "data": {"active": False},
        "where": [["user_id", "=", user_id], ["active", "=", True]]
    }
    updated = update(payload)
    if not updated:
        return None
    return updated[0]["user_id"]


def create_user(user_personal_data: dict, password: str) -> int:
    data = create({"table": "user_personal", "data": user_personal_data})
    user_id = data[0]["user_id"]

    # Add authentication password
    add_password(user_id, password)

    return user_id

