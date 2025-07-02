import asyncio
import psutil
import json
from datetime import datetime
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import Message


async def get_sensor_data():
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "cpu_usage": psutil.cpu_percent(interval=None),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    }


async def main():
    print("Connecting as system_reader module...")
    client = IoTHubModuleClient.create_from_edge_environment()
    await client.connect()
    print("Connected. Sending telemetry to cloud_publisher...")

    try:
        while True:
            data = await get_sensor_data()
            message = Message(json.dumps(data))
            await client.send_message_to_output(message, "readerOutput")
            await asyncio.sleep(5)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.shutdown()

if __name__ == "__main__":
    asyncio.run(main())