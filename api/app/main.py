import asyncio
from fastapi import FastAPI
from dotenv import load_dotenv
from app.routes.status import router as status_router
from app.routes.commands import router as commands_router
from app.eventhub_consumer import consume

from fastapi import FastAPI, Depends, Security
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowAuthorizationCode

from app.auth import oauth2_scheme, CLIENT_ID, SCOPE

load_dotenv()


app = FastAPI(
    swagger_ui_init_oauth={
        "clientId": CLIENT_ID,
        "scopes": SCOPE,
        "usePkceWithAuthorizationCodeGrant": True,
    }
)
app.include_router(status_router)
app.include_router(commands_router)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume())