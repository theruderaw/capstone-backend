from crud import create,read,update,delete
from typing import Optional

def get_finances_self(user_id,dashboard:bool):
    rows = ["uf.userfinance_id as id","up.base_wage as base_wage","up.penalty_per_unit as penalty_per_unit","uf.user_id as user_id","up.name as name","work_date","uf.hours_worked","uf.penalties_observed","up.status_id","uf.validated","uf.paid"]
    table = "user_finance uf JOIN user_personal up ON uf.user_id = up.user_id JOIN status st ON up.status_id = st.status_id"
    where = [["uf.user_id","=",user_id],["paid","=",False]]
    payload = {
        "table":table,
        "rows":rows,
        "where":where,
        "order_by":[["uf.userfinance_id","ASC"]]
    }
    if dashboard:
        payload["limit"] = 5
    
    return read(payload)

def submit_finance_entry(user_id: int, hours: int, penalties: int):
    db_payload = {
        "table": "user_finance",
        "data": {
            "user_id": user_id,
            "hours_worked": hours,
            "penalties_observed": penalties
        }
    }

    return create(db_payload)

def validated_finances(user_id:int,payment_id:int):
    payload = {
        "table":"user_finance",
        "data":{
            "validated":True,
            "validated_by":user_id
        },
        "where":[["userfinance_id","=",payment_id]]
    }
    return update(payload)

def authorise_finances(user_id,payment_id):
    payload = {
        "table":"user_finance",
        "data":{
            "authorized_by":user_id,
            "paid":True
        },
        "where":[["userfinance_id","=",payment_id]]
    }

    return update(payload)


def get_all_finances(
    validated: Optional[bool] = None,
    pending: Optional[bool] = None,
    order: bool = True
):
    rows = [
        "uf.userfinance_id as id",
        "uf.work_date",
        "uf.user_id",
        "up.name",
        "uf.hours_worked as hours",
        "uf.penalties_observed as penalties",
        "uf.paid",
        "uf.validated"
    ]

    table = """
        user_finance as uf
        JOIN user_personal as up ON up.user_id = uf.user_id
    """

    where = []

    if validated is not None:
        where.append(["uf.validated", "=", validated])

    if pending is not None:
        where.append(["uf.paid", "=", not pending])  # pending=True → paid=False

    order_by = [["uf.userfinance_id", "ASC" if order else "DESC"]]

    payload = {
        "table": table,
        "rows": rows,
        "where": where,
        "order_by": order_by
    }

    data = read(payload)
    return data