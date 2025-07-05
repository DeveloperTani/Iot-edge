import os
from dotenv import load_dotenv
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub import EventData
from app.state import latest_status

load_dotenv()

EVENT_HUB_CONN_STR = os.getenv("EVENT_HUB_CONNECTION_STRING")
EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME")

async def on_event(partition_context, event: EventData):
    try:
        status = event.body_as_json()
        device_id = status.get("device_id")

        print(f"Received event: {status} from partition: {partition_context.partition_id}")

        if device_id:
            latest_status[device_id] = status  # store status per device_id
            print(f"Updated latest_status for {device_id}: {latest_status[device_id]}")
        else:
            print("Warning: Missing device_id in status payload.")

        await partition_context.update_checkpoint(event)

    except Exception as e:
        print("Error in on_event:", e)

async def consume():
    if not EVENT_HUB_CONN_STR or not EVENT_HUB_NAME:
        raise RuntimeError("Missing Event Hub configuration.")
    
    client = EventHubConsumerClient.from_connection_string(
        conn_str=EVENT_HUB_CONN_STR,
        consumer_group="$Default",
        eventhub_name=EVENT_HUB_NAME,
    )
    async with client:
        await client.receive(on_event=on_event, starting_position="-1")