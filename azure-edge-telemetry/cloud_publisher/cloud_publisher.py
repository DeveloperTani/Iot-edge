import asyncio
import json
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import Message


async def message_handler(message):
    try:
        print(f"[cloud_publisher] Received message on publisherInput: {message.data}")
        print(f"[cloud_publisher] Raw payload: {message.data}")
        print(f"[cloud_publisher] Payload type: {type(message.data)}")git 

        # Defensive: confirm message.data is bytes or str
        payload = message.data
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")

        data = json.loads(payload)
        iothub_message = Message(json.dumps(data))

        await module_client.send_message_to_output(iothub_message, "publisherOutput")
        print("[cloud_publisher] Forwarded to IoT Hub.")

    except Exception as e:
        print(f"[cloud_publisher] Error in message_handler: {e}")


async def main():
    global module_client
    print("Connecting as cloud_publisher module...")
    module_client = IoTHubModuleClient.create_from_edge_environment()
    await module_client.connect()


    module_client.on_message_received = {
        "publisherInput": message_handler
    }

    print("Waiting for messages on publisherInput...")

    try:
        while True:
            await asyncio.sleep(1000)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await module_client.shutdown()

if __name__ == "__main__":
    asyncio.run(main())