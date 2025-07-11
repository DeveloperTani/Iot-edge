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
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))  # Default MQTT port for TLS
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
CA_CERT_PATH="/etc/ssl/certs/ca-certificates.crt"

MQTT_TOPIC = "iot/esp32c3/status"       # Incoming telemetry from ESP32
MQTT_COMMAND_TOPIC = "iot/esp32c3/cmd"  # Commands sent back to ESP32

latest_payload = None
last_sent_time = 0
SEND_INTERVAL = int(os.getenv("SEND_INTERVAL", "15"))

# --- MQTT Setup ---
def on_mqtt_message(client, userdata, message):
    global latest_payload
    try:
        payload = json.loads(message.payload.decode())
        payload["timestamp"] = datetime.utcnow().isoformat() + "Z"
        latest_payload = payload
        print(f"[MQTT IN] {payload}")
    except Exception as e:
        print(f"Failed to parse MQTT message: {e}")

def start_mqtt_loop():
    client = mqtt.Client()

    # TLS setup
    ca_cert_path = os.getenv("CA_CERT_PATH")
    if ca_cert_path:
        client.tls_set(ca_certs=ca_cert_path)
        client.tls_insecure_set(False) 
        print(f"[MQTT] TLS enabled using CA: {ca_cert_path}")
    else:
        print("[MQTT] TLS not enabled (CA_CERT_PATH missing)")

    client.username_pw_set(
        username=os.getenv("MQTT_USERNAME", ""),
        password=os.getenv("MQTT_PASSWORD", "")
    )

    client.on_message = on_mqtt_message
    client.connect(MQTT_BROKER, int(os.getenv("MQTT_PORT", 8883)), 60)
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

    try:
        name = method_request.name
        payload = method_request.payload if isinstance(method_request.payload, dict) else {}
        response_payload = {}

        if name == "set":
            new_temp = payload.get("target_temp")
            if new_temp is not None:
                target_temp = int(new_temp)
                send_mqtt_command(mqtt_client, "set", target_temp)
                response_payload = {"result": "success",}
                print(f"[METHOD] Set target temp to {target_temp}")
                status = 200
            else:
                raise ValueError("target_temp missing")

        elif name == "increase":
            send_mqtt_command(mqtt_client, "increase")
            response_payload = {"result": "success"}
            print(f"[METHOD] Forwarded 'increase' command")
            status = 200

        elif name == "decrease":
            send_mqtt_command(mqtt_client, "decrease")
            response_payload = {"result": "success",}
            print(f"[METHOD] Forwarded 'decrease' command")
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
                message = Message(json.dumps(latest_payload))  # send it as-is
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
