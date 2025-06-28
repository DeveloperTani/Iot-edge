import json
from azure.iot.device import IoTHubModuleClient, Message
import time


def message_handler(message):
    print(f"Received message on publisherInput: {message.data}")
    try:
        payload = json.loads(message.data)
        iothub_message = Message(json.dumps(payload))
        module_client.send_message(iothub_message, "publisherOutput")
        print("Forwarded to IoT Hub.")
    except Exception as e:
        print(f"Failed to process message: {e}")



def main():
    global module_client
    print("Connecting as cloud_publisher module...")
    module_client = IoTHubModuleClient.create_from_edge_environment()
    module_client.connect()
    module_client.on_message_received = message_handler
    print("Waiting for messages on publisherInput...")

    try:
        while True:
            time.sleep(1000)  # Keep alive
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        module_client.disconnect()

if __name__ == "__main__":
    main()