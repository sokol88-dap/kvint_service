import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from pymongo import AsyncMongoClient

from config import Settings
from consumer import run_consumer
from models import Call, ErrorResponse

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()

    async with AsyncMongoClient(
        str(settings.mongo_url), tz_aware=True, serverSelectionTimeoutMS=5000
    ) as mongo:
        db = mongo["calls_service"]
        await db.campaigns.create_index("campaign_id", unique=True)
        await db.calls.create_index("call_id", unique=True)
        await db.calls.create_index("campaign_id")
        app.state.db = db

        async with run_consumer(db, settings):
            yield


app = FastAPI(title="Campaign calls", lifespan=lifespan)


@app.get(
    "/campaigns/{campaign_id}/calls",
    response_model=list[Call],
    responses={
        200: {"model": list[Call], "description": "Campaign calls"},
        404: {"model": ErrorResponse, "description": "Campaign not found"},
    },
)
async def get_calls(campaign_id: str, request: Request):
    db = request.app.state.db
    if not await db.campaigns.find_one({"campaign_id": campaign_id}):
        raise HTTPException(status_code=404, detail="Campaign not found")

    return (
        await db.calls.find({"campaign_id": campaign_id}, {"_id": 0})
        .sort("call_id", 1)
        .to_list()
    )
