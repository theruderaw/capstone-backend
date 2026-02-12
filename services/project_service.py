from crud import create,update,delete,read
from datetime import datetime
from typing import List

def create_project(name:str,description:str,created_by:int):
    db_payload = {
        "table":"project",
        "data":{
            "name":name,
            "description":description,
            "created_at": datetime.now(),
            "created_by": created_by
        }
    }
    return create(db_payload)

def assign_members(project_id:int,manager_id:int,supervisor_id:int,workers:List[int]):
    db_payload =[{
        "table" : "project_assignment",
        "data":{
            "project_id":project_id,
            "user_id":manager_id,
            "is_manager":True
        }
    },{
        "table" : "project_assignment",
        "data":{
            "project_id":project_id,
            "user_id":supervisor_id,
            "is_supervisor":True
        }
    }]
    for worker_id in workers:
        db_payload.append({
            "table": "project_assignment",
            "data":{
                "project_id":project_id,
                "user_id":worker_id
            }
        })
    return [create(payload) for payload in db_payload]

def add_members(project_id:int,workers_id:int,supervisor:int|None = None):
    db_payload = [{
        "table":"project_assignment",
        "data":{
            "project_id":project_id,
            "user_id": worker_id,
            "is_supervisor": worker_id == supervisor
        }
    } for worker_id in workers_id]
    return [create(payload) for payload in db_payload]

def remove_members(workers_id):
    db_payload = [{
        "table":"project_assignment",
        "where":[["user_id","=",worker_id]]
    } for worker_id in workers_id]
    return [delete(payload) for payload in db_payload]

def get_project(project_id):
    db_payload = {
            "rows": [
                "p.project_id",
                "p.name AS project_name",
                "up.name AS project_manager"
            ],
            "table": "project p ""JOIN user_personal up ON p.created_by = up.user_id",
            "where": [["p.project_id", "=", project_id]],
            "order_by": [
                ["p.project_id","ASC"]
            ]
        }
    
    return read(db_payload)

def get_project_by_user_id(user_id):
    db_payload = {
        "rows":["project_id"],
        "table":"project_assignment",
        "where":[["user_id","=",user_id]]
    }
    return read(db_payload)

def get_members(project_id):
    db_payload = {
        "rows":["u.user_id","u.name",'s.name as "role"'],
        "table":"project_assignment pa join user_personal u ON pa.user_id = u.user_id join status s ON u.status_id = s.status_id",
        "where":[["pa.project_id","=",project_id]] 
    }
    return read(db_payload)

def get_project_by_supervisor_id(user_id):
    db_payload = {
        "rows":["project_id"],
        "table":"project_assignment",
        "where":[["user_id","=",user_id],["is_supervisor","=",True]]
    }
    return read(db_payload)

def get_project_by_manager_id(user_id):
    db_payload = {
        "rows":["project_id"],
        "table":"project_assignment",
        "where":[["user_id","=",user_id],["is_manager","=",True]]
    }
    return read(db_payload)
