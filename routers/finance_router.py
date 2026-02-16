from fastapi import APIRouter,HTTPException,Query
from auth import get_status,require_perm
from services.finance_service import reject_finance,get_all_finances,get_finances_self,submit_finance_entry,validated_finances,authorise_finances
from schemas import FinanceCreate,UserAction
from typing import Optional
import logging

router = APIRouter(
    prefix="/finances",
    tags=["finances"]
)

@router.get("/{user_id}",summary="Get pending finances for a specific user")
def get_finances(user_id:int,dashboard:bool=False):
    status = get_status(user_id)
    
    require_perm(status,1)
    try:
        data = get_finances_self(user_id,dashboard=dashboard)
        
        return {
            "status":"OK",
            "data":data if data else []
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")

@router.post("/{user_id}")
def submit_payment(user_id: int, finance: FinanceCreate):

    status = get_status(user_id)
    require_perm(status,3)

    try:
        inserted = submit_finance_entry(
            user_id=user_id,
            hours=finance.hours,
            penalties=finance.penalties
        )

        return {"status": "OK", "inserted": inserted}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.patch("/{payment_id}/validate",summary="Validate a finance entry")
def validate_payment(payment_id,payload:UserAction):
    status = get_status(payload.user_id)
    require_perm(status,5)
    
    try:
        data = validated_finances(
            user_id=payload.user_id,
            payment_id=payment_id
        )
        if not data:
            raise HTTPException(404)
        return {
            "result":"OK",
            "edited":data
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")

@router.patch("/{payment_id}/authorize",summary="Authorize / mark a finance entry as paid")
def auth_payment(payment_id,payload:UserAction):
    status = get_status(payload.user_id)
    
    require_perm(status,6)
    try:
        data = authorise_finances(
            user_id=payload.user_id,
            payment_id=payment_id
        )
        if not data:
            raise HTTPException(404)
        return {
            "result":"OK",
            "edited":data
        }
    except Exception as e:
        raise HTTPException(status_code=403,detail=f"{e}")

@router.patch("/{payment_id}/reject",summary="Reject a finance entry as paid")
def reject_payment(payment_id,payload:UserAction):
    status = get_status(payload.user_id)
    
    require_perm(status,5)
    try:
        data = reject_finance(
            user_id=payload.user_id,
            payment_id=payment_id
        )
        if not data:
            raise HTTPException(404)
        return {
            "result":"OK",
            "edited":data
        }
    except Exception as e:
        raise HTTPException(status_code=403,detail=f"{e}")

@router.get("/", summary="Get all finances with optional filters")
def get_finances_all(
    user_id: int = Query(...),
    validated: Optional[str] = Query(None),  # accept as string
    pending: Optional[str] = Query(None),
    order: bool = True
):
    print("Here")
    status = get_status(user_id)
    require_perm(status, 2)
    print("Status:", status)

    # Convert validated / pending to bool manually
    val_bool = validated.lower() == "true" if validated is not None else None
    pend_bool = pending.lower() == "true" if pending is not None else None

    data = get_all_finances(
        validated=val_bool,
        pending=pend_bool,
        order=order
    )
    print("Data:", data)
    return {"status": "OK", "data": data}