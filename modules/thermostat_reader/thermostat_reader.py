import asyncio
import json
import os
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import Message, MethodResponse

# MQTT settings
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = 1883
MQTT_TOPIC = "iot/esp32c3/status"

latest_payload = None
last_sent_time = 0
SEND_INTERVAL = int(os.getenv("SEND_INTERVAL", "15"))
target_temp = int(os.getenv("TARGET_TEMP", "23"))  # Optional override

# MQTT client setup
def on_mqtt_message(client, userdata, message):
    global latest_payload
    try:
        payload = json.loads(message.payload.decode())
        payload["timestamp"] = datetime.utcnow().isoformat() + "Z"
        payload["target_temp"] = target_temp  # Inject latest target temp
        latest_payload = payload
        print(f"MQTT message: {payload}")
    except Exception as e:
        print(f"Failed to parse MQTT: {e}")

def start_mqtt_loop():
    client = mqtt.Client()
    client.on_message = on_mqtt_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC)
    client.loop_start()
    return client

# Direct method handlerasync 
async def method_handler(method_request, client):
    global target_temp
    if method_request.name == "set":
        try:
            payload = method_request.payload
            new_temp = payload.get("target_temp")
            if new_temp is not None:
                target_temp = new_temp
                print(f"Target temperature updated to {target_temp}")
                response = MethodResponse.create_from_method_request(
                    method_request,
                    status=200,
                    payload={"result": "success", "target_temp": target_temp}
                )
            else:
                raise ValueError("target_temp missing in payload")
        except Exception as e:
            response = MethodResponse.create_from_method_request(
                method_request,
                status=400,
                payload={"error": str(e)}
            )
        await client.send_method_response(response)
    elif method_request.name == "increase":
        target_temp += 1
        print(f"Target temperature increased to {target_temp}")
        response = MethodResponse.create_from_method_request(
            method_request,
            status=200,
            payload={"result": "success", "target_temp": target_temp}
        )
        await client.send_method_response(response)
    
    elif method_request.name == "decrease":
        target_temp -= 1
        print(f"Target temperature decreased to {target_temp}")
        response = MethodResponse.create_from_method_request(
            method_request,
            status=200,
            payload={"result": "success", "target_temp": target_temp}
        )
        await client.send_method_response(response)

# Main loop
async def main():
    global last_sent_time, method_client
    print("Starting thermostat_reader module...")
    mqtt_client = start_mqtt_loop()

    method_client = IoTHubModuleClient.create_from_edge_environment()
    await method_client.connect()
    print("Connected to IoT Edge runtime.")

    # Register direct method
    async def on_method_request(req):
        await method_handler(req, method_client)

    method_client.on_method_request_received = on_method_request
    try:
        while True:
            now = time.time()
            if latest_payload and (now - last_sent_time >= SEND_INTERVAL):
                message = Message(json.dumps(latest_payload))
                await method_client.send_message_to_output(message, "thermostatOutput")
                last_sent_time = now
                print("Sent to output:", latest_payload)
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await method_client.shutdown()
        mqtt_client.loop_stop()

if __name__ == "__main__":
    asyncio.run(main())
