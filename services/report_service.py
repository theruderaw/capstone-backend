from crud import create,read,update
from typing import Optional

def submit_report(reason:str,description:str,submission_date:str,user_id:str):
    db_payload = {
        "table":"reports",
        "data":{
            "user_id":user_id,
            "report_date":submission_date,
            "reason":reason,
            "report_content":description
        }
    }

    return create(db_payload)

def get_report_summary(supervisor_id:int):
    db_payload = {
        "rows" : [
            "r.id",
            "u.name",
            "r.reason"
        ],
        "table" : "reports r JOIN user_personal u ON r.user_id = u.user_id",
        "where" : [["u.supervisor","=",supervisor_id]]
    }
    return read(db_payload)

def resolve_issue(supervisor_id:int,report_id:int,res_date:int,remarks:str):
    db_payload = {
        "table":"resolution",
        "data":{
            "report_id":report_id,
            "supervisor_id":supervisor_id,
            "resolution_date":res_date,
            "remarks":remarks
        }
    }
    return create(db_payload)

def mark_resolved(report_id):
    db_payload = {
        "table":"reports",
        "data": {
            "resolved":True
        },
        "where": [["id","=",report_id]]
    }
    return update(db_payload)

def watch_report_manager(manager_id:int,resolved:Optional[bool]):
    db_payload = {
        "rows": [
            "w.name AS worker_name",
            "s.name AS supervisor_name",
            "r.id",
            "r.report_date",
            "r.reason",
            "r.report_content",
            "res.remarks"
        ],
        "table" : "reports r JOIN user_personal w ON r.user_id = w.user_id LEFT JOIN user_personal s ON w.supervisor = s.user_id LEFT JOIN resolution res ON r.id = res.report_id",
        "where": [["s.supervisor","=",manager_id]]
    }
    if resolved:
        db_payload["where"].append(["r.status","<>",True])
    return read(db_payload)

def watch_report_supervisor(supervisor_id:int,resolved:Optional[bool]):
    db_payload = {
        "rows": [
            "w.name AS worker_name",
            "s.name AS supervisor_name",
            "r.id",
            "r.report_date",
            "r.reason",
            "r.report_content",
            "res.remarks"
        ],
        "table" : "reports r JOIN user_personal w ON r.user_id = w.user_id LEFT JOIN user_personal s ON w.supervisor = s.user_id LEFT JOIN resolution res ON r.id = res.report_id",
        "where": [["w.supervisor","=",supervisor_id]]
    }
    if resolved:
        db_payload["where"].append(["r.status","<>",True])
    return read(db_payload)

def get_report(report_id:int):
    db_payload = {
        "rows": [
            "w.name AS worker_name",
            "s.name AS supervisor_name",
            "r.id",
            "r.report_date",
            "r.reason",
            "r.report_content",
            "res.remarks"
        ],
        "table" : "reports r JOIN user_personal w ON r.user_id = w.user_id LEFT JOIN user_personal s ON w.supervisor = s.user_id LEFT JOIN resolution res ON r.id = res.report_id",
        "where" : [["r.id","=",report_id]]
    }
    return read(db_payload)

def get_resolved(report_id:int):
    """SELECT EXISTS (
    SELECT 1 
    FROM resolution
    WHERE report_id = 6
);"""
    db_payload = {
        "query" : f"SELECT EXISTS (SELECT 1 FROM resolution WHERE report_id={report_id})"
    }
    data = read(db_payload)
    return data