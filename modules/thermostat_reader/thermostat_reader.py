import asyncio
import json
import os
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import Message

# MQTT settings
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = 1883
MQTT_TOPIC = "iot/esp32c3/status"

latest_payload = None
last_sent_time = 0
SEND_INTERVAL = int(os.getenv("SEND_INTERVAL", "15"))

# MQTT client setup
def on_mqtt_message(client, userdata, message):
    global latest_payload
    try:
        payload = json.loads(message.payload.decode())
        payload["timestamp"] = datetime.utcnow().isoformat() + "Z"
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

# Main loop
async def main():
    global last_sent_time
    print("Starting thermostat_reader module...")
    mqtt_client = start_mqtt_loop()

    client = IoTHubModuleClient.create_from_edge_environment()
    await client.connect()
    print("Connected to IoT Edge runtime.")

    try:
        while True:
            now = time.time()
            if latest_payload and (now - last_sent_time >= SEND_INTERVAL):
                message = Message(json.dumps(latest_payload))
                await client.send_message_to_output(message, "thermostatOutput")
                last_sent_time = now
                print("Sent to output:", latest_payload)
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.shutdown()
        mqtt_client.loop_stop()

if __name__ == "__main__":
    asyncio.run(main())