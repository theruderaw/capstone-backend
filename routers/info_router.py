# routers/info.py
from fastapi import APIRouter, HTTPException
from auth import get_status, require_perm
from services.info_service import set_office,set_onsite,status_of_worker,set_working,get_user_info,get_supervisor,reset_working
from ws import broadcast_status_change

router = APIRouter(prefix="/info", tags=["Info"])

@router.get("/",summary="Get activity status of worker")
def worker_active(user_id:int):
    status = get_status(user_id)
    require_perm(status,1)

    try:
        data = status_of_worker(user_id)
        if not data:
            raise HTTPException(404,"User not found")
        return {
            "status":"OK",
            "data":data[0]
        }
    except Exception as e:
        raise HTTPException(500,f"{e}")

@router.get("/user", summary="Get personal info for a user")
def user_info(user_id: int):
    status = get_status(user_id)
    require_perm(status, 1)

    try:
        info = get_user_info(user_id)
        return {"status": "OK", "data": info}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/supervisor",summary="Get supervisor info for a user")
def get_supervisor_data(user_id:int):
    status = get_status(user_id)
    require_perm(status,1)

    try:
        data = get_supervisor(user_id)
        return {
            "status":"OK",
            "data": data[0] if data else None
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")

@router.post("/break", summary="Set worker inactive")
async def go_break(user_id: int):
    status = get_status(user_id)
    require_perm(status, 1)

    try:
        data = reset_working(user_id)
        if not data:
            raise HTTPException(404, "User not found")

        # Broadcast the status change to all subscribers of this user
        await broadcast_status_change(user_id, {
            "event": "status_change",
            "user_id": user_id,
            "status": "break"
        })

        return {
            "status": "OK",
            "data": data
        }

    except Exception as e:
        raise HTTPException(500, f"{e}")

@router.post("/working", summary="Set worker active")
async def go_working(user_id: int):
    status = get_status(user_id)
    require_perm(status, 1)

    try:
        data = set_working(user_id)
        if not data:
            raise HTTPException(404, "User not found")

        # Broadcast the status change to all subscribers of this user
        await broadcast_status_change(user_id, {
            "event": "status_change",
            "user_id": user_id,
            "status": "working"
        })

        return {
            "status": "OK",
            "data": data
        }

    except Exception as e:
        raise HTTPException(500, f"{e}")

@router.post("/onsite", summary="Set worker inactive")
async def go_onsite(user_id: int):
    status = get_status(user_id)
    require_perm(status, 1)

    try:
        data = set_onsite(user_id)
        if not data:
            raise HTTPException(404, "User not found")

        # Optional: Broadcast onsite status
        await broadcast_status_change(user_id, {
            "event": "location_change",
            "user_id": user_id,
            "location": "onsite"
        })

        return {
            "status": "OK",
            "data": data
        }

    except Exception as e:
        raise HTTPException(500, f"{e}")

@router.post("/offsite", summary="Set worker active")
async def go_offste(user_id: int):
    status = get_status(user_id)
    require_perm(status, 1)

    try:
        data = set_office(user_id)
        if not data:
            raise HTTPException(404, "User not found")

        # Optional: Broadcast offsite status
        await broadcast_status_change(user_id, {
            "event": "location_change",
            "user_id": user_id,
            "location": "offsite"
        })

        return {
            "status": "OK",
            "data": data
        }

    except Exception as e:
        raise HTTPException(500, f"{e}")