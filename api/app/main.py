import asyncio
from fastapi import FastAPI
from dotenv import load_dotenv
from app.routes.status import router as status_router
from app.routes.commands import router as commands_router
from app.eventhub_consumer import consume

load_dotenv()

app = FastAPI()
app.include_router(status_router)
app.include_router(commands_router)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume())