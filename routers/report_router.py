from fastapi import APIRouter,HTTPException,Query
from services.report_service import get_resolved,submit_report,get_report_summary,resolve_issue,watch_report_manager,watch_report_supervisor,get_report,mark_resolved
from schemas import ReportSubmission,ResolveReport
from typing import Optional
from auth import get_status,require_perm

router = APIRouter(
    prefix="/report",
    tags=["Report"]
)

@router.post("/submit")
def submit_report_data(payload:ReportSubmission):
    status = get_status(payload.user_id)
    require_perm(status,1)
    try:
        data = submit_report(
            reason=payload.reason,
            description=payload.description,
            submission_date=payload.submission_date,
            user_id=payload.user_id
        )
        return {"status":"OK","data":data}
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")
    
@router.get("/")
def get_supervisor_reports(user_id:int):
    status = get_status(user_id)
    require_perm(status,2)
    try:
        data = get_report_summary(user_id)
        return {
            "status":"OK",
            "data":data if data else []
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")
    
@router.put("/{report_id}/resolve")
def resolve(report_id:int,payload:ResolveReport):
    status = get_status(payload.supervisor_id)
    require_perm(status,7)
    try:
        if get_resolved(report_id)[0]['exists']:
            raise HTTPException(status_code=400,detail="Already Resolved")
        data = resolve_issue(
            supervisor_id=payload.supervisor_id,
            report_id=report_id,
            res_date=payload.res_date,
            remarks=payload.remarks
        )
        if data:
            resolution = mark_resolved(report_id=report_id)
        return {
            "status":"OK",
            "data":data if data else [],
            "resolution":data[0].get("resolution_id",0)
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")
    
@router.get("/summary")
def summarize_report(user_id:int,resolved:Optional[bool] = Query(default=None)):
    status = get_status(user_id)
    if status not in {2,3}:
        raise HTTPException(status_code=403,detail="Forbidden")
    try:
        if status == 3:
            data = watch_report_manager(user_id,resolved=resolved)
        else:
            data = watch_report_supervisor(user_id,resolved=resolved)
        return {
            "status":"OK",
            "data":data if data else []
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")
    
@router.get("/{report_id}")
def get_report_by_id(report_id:int,user_id:int):
    status = get_status(user_id)
    require_perm(status,1)
    try:
        data = get_report(report_id)
        return {
            "status":"OK",
            "data":data if data else []
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"{e}")