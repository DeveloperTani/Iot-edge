from fastapi import APIRouter, Request, HTTPException, Security
from app.auth import oauth2_scheme

router = APIRouter()

# 1. General status overview via MQTT
@router.get("", dependencies=[Security(oauth2_scheme)])
def get_all_status(request: Request):
    status = request.app.state.latest_mqtt_status
    print("Returned from /status:", status)
    if status:
        return status
    return {"message": "No status available yet"}

# 2. Status for a specific device via MQTT
@router.get("/{device_id}", dependencies=[Security(oauth2_scheme)])
def get_mqtt_status(device_id: str, request: Request):
    status_data = request.app.state.latest_mqtt_status.get(device_id)
    if not status_data:
        raise HTTPException(status_code=404, detail="No status available for this device")
    return status_data