import time
import psutil
import json
import os
from datetime import datetime
from azure.iot.device import IoTHubDeviceClient, Message
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Load connection string securely from environment
CONNECTION_STRING = os.getenv("IOTHUB_CONNECTION_STRING")

if not CONNECTION_STRING:
    raise ValueError("IOTHUB_CONNECTION_STRING is not set in environment.")

def get_sensor_data():
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "cpu_usage": psutil.cpu_percent(interval=1),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    }

def main():
    print("Connecting to Azure IoT Hub...")
    device_client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    device_client.connect()
    print("Connected. Sending data...")

    try:
        while True:
            data = get_sensor_data()
            message = Message(json.dumps(data))
            device_client.send_message(message)
            print(f"Sent: {data}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        device_client.disconnect()

if __name__ == "__main__":
    main()