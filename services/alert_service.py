from crud import create, read
import logging

logger = logging.getLogger("myapp")

async def create_and_broadcast_alert(severity_id: int, worker_id: int = None):
    """
    Create alert and notify:
    1. Worker's direct supervisor (view-only: can_resolve=false, can_remove=false)
    2. Supervisor's supervisor if exists (can dismiss: can_remove=true)
    3. IT/Admin via topic (can resolve: can_resolve=true)
    """
    try:
        # Get severity name
        severity_payload = {
            "table": "severity_levels",
            "rows": ["level_name"],
            "where": [["id", "=", severity_id]]
        }
        severity_result = read(severity_payload)
        severity_name = severity_result[0]["level_name"] if severity_result else "Unknown"

        # Create default message based on severity
        default_message = f"{severity_name} alert triggered by worker {worker_id}"

        # Insert alert into database
        insert_payload = {
            "table": "alerts",
            "data": {
                "severity_id": severity_id,
                "message": default_message,
                "action": "System alert",
                "worker_id": worker_id,
                "resolved": False
            }
        }
        insert_result = create(insert_payload)
        if not insert_result:
            raise ValueError("Failed to insert alert into database")
        
        alert_id = insert_result[0]["id"]
        created_at = insert_result[0]["created_at"]

        # Build base alert payload
        alert_data = {
            "event": "system_alert",
            "alert_id": alert_id,
            "severity_id": severity_id,
            "worker_id": worker_id
        }

        # Get supervisor chain using CRUD
        supervisor_id = None
        supervisor_supervisor_id = None

        if worker_id:
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
                    logger.info(f"Alert {alert_id}: Found supervisor {supervisor_id} for worker {worker_id}")

                    # Get supervisor's supervisor (if exists)
                    if supervisor_id:
                        sup_payload = {
                            "table": "user_personal",
                            "rows": ["supervisor"],
                            "where": [["user_id", "=", supervisor_id]]
                        }
                        sup_result = read(sup_payload)
                        if sup_result and sup_result[0]["supervisor"]:
                            supervisor_supervisor_id = sup_result[0]["supervisor"]
                            logger.info(f"Alert {alert_id}: Found supervisor's supervisor {supervisor_supervisor_id}")
                else:
                    logger.warning(f"Alert {alert_id}: Worker {worker_id} has no supervisor")

            except Exception as e:
                logger.error(f"Error fetching supervisor chain for worker {worker_id}: {e}")

        # Broadcast to WebSocket manager
        from ws import manager

        supervisor_sent = False

        # Send to direct supervisor (view-only)
        if supervisor_id:
            supervisor_alert = {**alert_data, "can_resolve": False, "can_remove": False}
            await manager.send_to_user(supervisor_id, supervisor_alert)
            supervisor_sent = True
            logger.info(f"Alert {alert_id}: Sent to supervisor {supervisor_id} (view-only)")

        # Send to supervisor's supervisor if exists (can dismiss)
        if supervisor_supervisor_id:
            sup_sup_alert = {**alert_data, "can_resolve": False, "can_remove": True}
            await manager.send_to_user(supervisor_supervisor_id, sup_sup_alert)
            logger.info(f"Alert {alert_id}: Sent to supervisor's supervisor {supervisor_supervisor_id} (can dismiss)")

        # Fallback: if a direct supervisor was not found, publish the alert to all supervisors
        if not supervisor_sent and severity_id >= 3:
            await manager.publish("alerts_supervisors", {**alert_data, "can_resolve": False, "can_remove": False})
            logger.info(f"Alert {alert_id}: Published to alerts_supervisors fallback topic")

        # Broadcast to IT/Admin topic
        it_alert = {**alert_data, "can_resolve": True, "can_remove": False}
        await manager.publish("alerts_admin", it_alert)
        logger.info(f"Alert {alert_id}: Published to IT/Admin topic (can resolve)")

        return alert_id

    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        raise

