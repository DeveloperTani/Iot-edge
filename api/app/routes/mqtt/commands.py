from fastapi import APIRouter, HTTPException, Security, Request
from app.state import latest_mqtt_status
from app.auth import oauth2_scheme
import json
import os

router = APIRouter()

MQTT_CMD_TOPIC = os.getenv("MQTT_CMD_TOPIC", "iot/{device_id}/cmd")


def publish_command(request: Request, device_id: str, cmd: str, value: int = None):
    topic = MQTT_CMD_TOPIC.format(device_id=device_id)
    payload = {"cmd": cmd}
    if value is not None:
        payload["value"] = value

    mqtt_client = request.app.state.mqtt_client
    mqtt_client.publish(topic, json.dumps(payload))
    print(f"[MQTT OUT] Published to {topic}: {payload}")
    return payload


@router.post("/mqtt/command/{device_id}/increase", dependencies=[Security(oauth2_scheme)])
def increase_target_temp(device_id: str, request: Request):
    if device_id not in latest_mqtt_status:
        raise HTTPException(status_code=404, detail="Device not found or no status available")

    current_temp = latest_mqtt_status[device_id].get("target_temp")
    if current_temp is None:
        raise HTTPException(status_code=400, detail="Target temperature not available")

    new_temp = current_temp + 1
    publish_command(request, device_id, "increase")

    return {
        "device_id": device_id,
        "old_target_temp": current_temp,
        "new_target_temp": new_temp,
        "mqtt_topic": MQTT_CMD_TOPIC.format(device_id=device_id)
    }


@router.post("/mqtt/command/{device_id}/decrease", dependencies=[Security(oauth2_scheme)])
def decrease_target_temp(device_id: str, request: Request):
    if device_id not in latest_mqtt_status:
        raise HTTPException(status_code=404, detail="Device not found or no status available")

    current_temp = latest_mqtt_status[device_id].get("target_temp")
    if current_temp is None:
        raise HTTPException(status_code=400, detail="Target temperature not available")

    new_temp = current_temp - 1
    publish_command(request, device_id, "decrease")

    return {
        "device_id": device_id,
        "old_target_temp": current_temp,
        "new_target_temp": new_temp,
        "mqtt_topic": MQTT_CMD_TOPIC.format(device_id=device_id)
    }


@router.post("/mqtt/command/{device_id}/set/{target_temp}", dependencies=[Security(oauth2_scheme)])
def set_target_temp(device_id: str, target_temp: int, request: Request):
    if device_id not in latest_mqtt_status:
        raise HTTPException(status_code=404, detail="Device not found or no status available")

    current_temp = latest_mqtt_status[device_id].get("target_temp")
    if current_temp is None:
        raise HTTPException(status_code=400, detail="Target temperature not available")

    publish_command(request, device_id, "set", value=target_temp)

    return {
        "device_id": device_id,
        "old_target_temp": current_temp,
        "new_target_temp": target_temp,
        "mqtt_topic": MQTT_CMD_TOPIC.format(device_id=device_id)
    }