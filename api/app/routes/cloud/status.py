from app.state import latest_cloud_status
from fastapi import APIRouter
from fastapi import Security
from app.auth import oauth2_scheme

router = APIRouter()

# 1. General status overview via cloud

@router.get("", dependencies=[Security(oauth2_scheme)])
def get_all_status():
    print("Returned from /status:", latest_cloud_status)
    if latest_cloud_status:
        return latest_cloud_status
    return {"message": "No status available yet"}

# 2. Status for a specific device via cloud

@router.get("/status/{device_id}", dependencies=[Security(oauth2_scheme)])
def get_device_status(device_id: str):
    if device_id in latest_cloud_status:
        return latest_cloud_status[device_id]
    return {"message": f"No status available for device {device_id}"}