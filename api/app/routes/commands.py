from fastapi import APIRouter, HTTPException
from app.state import latest_status
from app.azure_method import invoke_direct_method
from app.device_map import AZURE_DEVICE_MAP
from fastapi import Security
from app.auth import oauth2_scheme


router = APIRouter()

from app.device_map import AZURE_DEVICE_MAP

# 1. Increase target temperature /command/{device_id}/increase

@router.post("/command/{device_id}/increase", dependencies=[Security(oauth2_scheme)])
def increase_target_temp(device_id: str):
    if device_id not in latest_status:
        raise HTTPException(status_code=404, detail="Device not found or no status available")

    current_temp = latest_status[device_id].get("target_temp")
    if current_temp is None:
        raise HTTPException(status_code=400, detail="Target temperature not set")

    new_temp = current_temp + 1

    device_info = AZURE_DEVICE_MAP.get(device_id)
    if not device_info:
        raise HTTPException(status_code=404, detail="Azure device mapping not found")

    result = invoke_direct_method(
        device_id=device_info["azure_device_id"],
        module_id=device_info["module_id"],
        method_name="increase",
        payload={}
    )

    return {
        "device_id": device_id,
        "azure_device_id": device_info["azure_device_id"],
        "module_id": device_info["module_id"],
        "old_target_temp": current_temp,
        "new_target_temp": new_temp,
        "cloud_response": result
    }

# 2. Decrease target temperature /command/{device_id}/decrease

@router.post("/command/{device_id}/decrease", dependencies=[Security(oauth2_scheme)])
def decrease_target_temp(device_id: str):
    if device_id not in latest_status:
        raise HTTPException(status_code=404, detail="Device not found or no status available")

    current_temp = latest_status[device_id].get("target_temp")
    if current_temp is None:
        raise HTTPException(status_code=400, detail="Target temperature not set")

    new_temp = current_temp - 1

    device_info = AZURE_DEVICE_MAP.get(device_id)
    if not device_info:
        raise HTTPException(status_code=404, detail="Azure device mapping not found")

    result = invoke_direct_method(
        device_id=device_info["azure_device_id"],
        module_id=device_info["module_id"],
        method_name="decrease",
        payload={}
    )

    return {
        "device_id": device_id,
        "azure_device_id": device_info["azure_device_id"],
        "module_id": device_info["module_id"],
        "old_target_temp": current_temp,
        "new_target_temp": new_temp,
        "cloud_response": result
    }

# 3. Set target temperature /command/{device_id}/set/{target_temp}

@router.post("/command/{device_id}/set/{target_temp}", dependencies=[Security(oauth2_scheme)])
def set_target_temp(device_id: str, target_temp: int):
    if device_id not in latest_status:
        raise HTTPException(status_code=404, detail="Device not found or no status available")

    current_temp = latest_status[device_id].get("target_temp")
    if current_temp is None:
        raise HTTPException(status_code=400, detail="Target temperature not set")

    device_info = AZURE_DEVICE_MAP.get(device_id)
    if not device_info:
        raise HTTPException(status_code=404, detail="Azure device mapping not found")

    result = invoke_direct_method(
        device_id=device_info["azure_device_id"],
        module_id=device_info["module_id"],
        method_name="set",
        payload={"target_temp": target_temp}
    )

    return {
        "device_id": device_id,
        "azure_device_id": device_info["azure_device_id"],
        "module_id": device_info["module_id"],
        "old_target_temp": current_temp,
        "new_target_temp": target_temp,
        "cloud_response": result
    }