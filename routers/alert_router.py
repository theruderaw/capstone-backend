from fastapi import APIRouter, HTTPException
from typing import Optional
from auth import get_status
from crud import update
from services.alert_service import create_and_broadcast_alert
import logging
from schemas import AlertCreate

logger = logging.getLogger("myapp")
router = APIRouter(prefix="/alert", tags=["Alerts"])


@router.post("/trigger", summary="Trigger a new system alert")
async def trigger_alert(payload: AlertCreate):
    """
    Trigger alert: Worker (1) or Supervisor (2) can trigger
    Notifies supervisor and supervisor's supervisor if exists, and IT/Admin
    """
    status = get_status(payload.user_id)
    if status not in [1, 2]:  # Worker or Supervisor
        raise HTTPException(403, "Not authorized to trigger alerts")

    try:
        alert_id = await create_and_broadcast_alert(
            severity_id=payload.severity_id,
            worker_id=payload.user_id
        )
        return {
            "status": "OK",
            "data": {
                "message": "Alert dispatched successfully",
                "alert_id": alert_id
            }
        }
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Error triggering alert: {e}")
        raise HTTPException(500, f"Internal server error")


@router.post("/resolve/{alert_id}", summary="Resolve an active alert (IT only)")
async def resolve_alert(alert_id: int, user_id: int):
    """
    Resolve alert: Only IT/Admin (status_id=5) can mark as resolved
    Sends acknowledgment message to all supervisors in the chain
    """
    status = get_status(user_id)
    if status != 5:  # Only IT/Admin
        raise HTTPException(403, "Only IT/Admin can resolve alerts")

    try:
        # Get alert details to find worker_id
        from crud import read
        alert_payload = {
            "table": "alerts",
            "rows": ["worker_id"],
            "where": [["id", "=", alert_id], ["resolved", "=", False]]
        }
        alert_result = read(alert_payload)
        if not alert_result:
            raise HTTPException(404, "Alert not found or already resolved")
        
        worker_id = alert_result[0]["worker_id"]

        # Use CRUD to update alert
        update_payload = {
            "table": "alerts",
            "data": {
                "resolved": True,
                "resolved_by": user_id
            },
            "where": [["id", "=", alert_id], ["resolved", "=", False]]
        }
        result = update(update_payload)
        
        if not result:
            raise HTTPException(404, "Alert not found or already resolved")

        # Get supervisor chain
        supervisors_to_notify = []
        try:
            # Get worker's direct supervisor
            worker_payload = {
                "table": "user_personal",
                "rows": ["supervisor"],
                "where": [["user_id", "=", worker_id]]
            }
            worker_result = read(worker_payload)
            if worker_result and worker_result[0]["supervisor"]:
                supervisor_id = worker_result[0]["supervisor"]
                supervisors_to_notify.append(supervisor_id)

                # Get supervisor's supervisor
                sup_payload = {
                    "table": "user_personal",
                    "rows": ["supervisor"],
                    "where": [["user_id", "=", supervisor_id]]
                }
                sup_result = read(sup_payload)
                if sup_result and sup_result[0]["supervisor"]:
                    supervisor_supervisor_id = sup_result[0]["supervisor"]
                    supervisors_to_notify.append(supervisor_supervisor_id)
        except Exception as e:
            logger.warning(f"Error fetching supervisor chain for alert {alert_id}: {e}")

        # Send acknowledgment message to all supervisors
        from ws import manager
        ack_message = {
            "event": "ack_message",
            "severity_id": 1,
            "message": "resolved",
            "alert_id": alert_id,
            "resolved_by": user_id
        }
        for supervisor_id in supervisors_to_notify:
            await manager.send_to_user(supervisor_id, ack_message)
            logger.info(f"Sent ack message for alert {alert_id} to supervisor {supervisor_id}")

        # Broadcast resolution to all viewers
        await manager.publish(alert_id, {
            "event": "alert_resolved",
            "alert_id": alert_id,
            "resolved_by": user_id
        })

        return {
            "status": "OK",
            "data": {
                "message": "Alert resolved successfully",
                "alert_id": alert_id
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        raise HTTPException(500, f"Internal server error")

