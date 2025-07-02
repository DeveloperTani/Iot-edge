import asyncio
import json
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import Message

module_client = None  

async def message_handler(message):
    print(f"[cloud_publisher] 🟢 Message received on input: {message.input_name}")
    try:
        payload = message.data
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")

        data = json.loads(payload)
        iothub_message = Message(json.dumps(data))

        await module_client.send_message_to_output(iothub_message, "publisherOutput")
        print("[cloud_publisher] ✅ Message forwarded to IoT Hub.")
    except Exception:
        pass 

async def main():
    global module_client
    module_client = IoTHubModuleClient.create_from_edge_environment()
    await module_client.connect()

    module_client.on_message_received = message_handler

    try:
        while True:
            await asyncio.sleep(60)
    except Exception:
        pass
    finally:
        await module_client.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        pass