import asyncio
import json
import os
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import Message, MethodResponse

# --- MQTT settings ---
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = 1883
MQTT_TOPIC = "iot/esp32c3/status"       # Incoming telemetry from ESP32
MQTT_COMMAND_TOPIC = "iot/esp32c3/cmd"  # Commands sent back to ESP32

latest_payload = None
last_sent_time = 0
SEND_INTERVAL = int(os.getenv("SEND_INTERVAL", "15"))
target_temp = int(os.getenv("TARGET_TEMP", "23"))  # Initial default target

# --- MQTT Setup ---
def on_mqtt_message(client, userdata, message):
    global latest_payload
    try:
        payload = json.loads(message.payload.decode())
        payload["timestamp"] = datetime.utcnow().isoformat() + "Z"
        payload["target_temp"] = target_temp
        latest_payload = payload
        print(f"[MQTT IN] {payload}")
    except Exception as e:
        print(f"Failed to parse MQTT message: {e}")

def start_mqtt_loop():
    client = mqtt.Client()
    client.on_message = on_mqtt_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC)
    client.loop_start()
    return client

def send_mqtt_command(client, cmd_type, value=None):
    cmd = {"cmd": cmd_type}
    if value is not None:
        cmd["value"] = value
    try:
        client.publish(MQTT_COMMAND_TOPIC, json.dumps(cmd))
        print(f"[MQTT OUT] Sent command: {cmd}")
    except Exception as e:
        print(f"Failed to send MQTT command: {e}")

# --- Direct Method Handler ---
async def method_handler(method_request, client, mqtt_client):
    global target_temp

    try:
        name = method_request.name
        payload = method_request.payload if isinstance(method_request.payload, dict) else {}
        response_payload = {}

        if name == "set":
            new_temp = payload.get("target_temp")
            if new_temp is not None:
                target_temp = int(new_temp)
                send_mqtt_command(mqtt_client, "set", target_temp)
                response_payload = {"result": "success", "target_temp": target_temp}
                print(f"[METHOD] Set target_temp to {target_temp}")
                status = 200
            else:
                raise ValueError("target_temp missing")

        elif name == "increase":
            target_temp += 1
            send_mqtt_command(mqtt_client, "increase")
            response_payload = {"result": "success", "target_temp": target_temp}
            print(f"[METHOD] Increased target_temp to {target_temp}")
            status = 200

        elif name == "decrease":
            target_temp -= 1
            send_mqtt_command(mqtt_client, "decrease")
            response_payload = {"result": "success", "target_temp": target_temp}
            print(f"[METHOD] Decreased target_temp to {target_temp}")
            status = 200

        else:
            print(f"[METHOD] Unknown method: {name}")
            response_payload = {"error": "Unknown method"}
            status = 404

    except Exception as e:
        print(f"[METHOD ERROR] {e}")
        response_payload = {"error": str(e)}
        status = 400

    response = MethodResponse.create_from_method_request(
        method_request, status=status, payload=response_payload
    )
    await client.send_method_response(response)

# --- Main async loop ---
async def main():
    global last_sent_time
    print("Starting thermostat_reader module...")
    mqtt_client = start_mqtt_loop()

    module_client = IoTHubModuleClient.create_from_edge_environment()
    await module_client.connect()
    print("Connected to IoT Edge runtime.")

    # Register direct method handler
    async def on_method_request(req):
        await method_handler(req, module_client, mqtt_client)

    module_client.on_method_request_received = on_method_request

    try:
        while True:
            now = time.time()
            if latest_payload and (now - last_sent_time >= SEND_INTERVAL):
                message = Message(json.dumps(latest_payload))
                await module_client.send_message_to_output(message, "thermostatOutput")
                print(f"[SEND] Telemetry sent: {latest_payload}")
                last_sent_time = now
            await asyncio.sleep(1)
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        await module_client.shutdown()
        mqtt_client.loop_stop()

if __name__ == "__main__":
    asyncio.run(main())
