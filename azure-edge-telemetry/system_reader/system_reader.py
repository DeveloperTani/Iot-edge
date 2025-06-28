import time
import psutil
import json
from datetime import datetime
from azure.iot.device import IoTHubModuleClient, Message

#Read sensor data using psutil

def get_sensor_data():
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "cpu_usage": psutil.cpu_percent(interval=1),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    }

# Main function to connect to IoT Hub and send telemetry data

def main():
    print("Connecting as system_reader module...")
    client = IoTHubModuleClient.create_from_edge_environment()
    client.connect()
    print("Connected. Sending telemetry to cloud_publisher...")

    try:
        while True:
            data = get_sensor_data()
            message = Message(json.dumps(data))
            client.send_message_to_output(message, "readerOutput") 
            time.sleep(5)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()