from fastapi import APIRouter
from app.state import latest_status

router = APIRouter()

# 1. General status overview

@router.get("/status")
def get_all_status():
    print("Returned from /status:", latest_status)
    if latest_status:
        return latest_status
    return {"message": "No status available yet"}

# 2. Status for a specific device

@router.get("/status/{device_id}")
def get_device_status(device_id: str):
    if device_id in latest_status:
        return latest_status[device_id]
    return {"message": f"No status available for device {device_id}"}