import os
import json
import paho.mqtt.client as mqtt
from app.state import latest_mqtt_status 

# Load MQTT config from environment
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
MQTT_CMD_TOPIC = os.getenv("MQTT_CMD_TOPIC")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
CA_CERT = os.getenv("CA_CERT_PATH", "/etc/ssl/certs/ca-certificates.crt")


def on_mqtt_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode())
        device_id = payload.get("device_id", "unknown")
        latest_mqtt_status[device_id] = payload
        print(f"[MQTT] Received from {device_id}: {payload}")
    except Exception as e:
        print(f"[MQTT ERROR] {e}")


def create_mqtt_client():
    client = mqtt.Client()
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set(ca_certs=CA_CERT)
    client.on_message = on_mqtt_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC)
    client.loop_start()
    return client
