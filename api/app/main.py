from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from app.auth import CLIENT_ID, SCOPE
from app.state import latest_mqtt_status
from app.mqtt.mqtt_client import create_mqtt_client
from app.azure.eventhub_consumer import consume
from app.routes.mqtt import status as mqtt_status
from app.routes.mqtt import commands as mqtt_cmds

import asyncio
import os

load_dotenv()

app = FastAPI(
    swagger_ui_init_oauth={
        "clientId": CLIENT_ID,
        "scopes": SCOPE,
        "usePkceWithAuthorizationCodeGrant": True,
    }
)


origins = os.getenv("ALLOWED_ORIGINS", "").split(",")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(mqtt_status.router, prefix="/mqtt/status")
app.include_router(mqtt_cmds.router, prefix="/mqtt/commands")

# Start MQTT + assign state
app.state.latest_mqtt_status = latest_mqtt_status
mqtt_client = create_mqtt_client()
app.state.mqtt_client = mqtt_client

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume())