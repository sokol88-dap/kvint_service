import asyncio
import logging
from contextlib import asynccontextmanager
from functools import partial

import aio_pika
from pydantic import ValidationError
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import PyMongoError

from config import Settings
from models import CallMessage

logger = logging.getLogger(__name__)


async def consume(message: aio_pika.IncomingMessage, db: AsyncDatabase) -> None:
    try:
        call = CallMessage.model_validate_json(message.body)
    except ValidationError as error:
        logger.warning("Invalid message: %s", error.errors(include_input=False))
        await message.reject(requeue=False)
        return

    try:
        await db.campaigns.update_one(
            {"campaign_id": call.campaign_id},
            {
                "$setOnInsert": {
                    "campaign_id": call.campaign_id,
                    "name": call.campaign_name or call.campaign_id,
                    "created_at": call.created_at,
                }
            },
            upsert=True,
        )
        await db.calls.update_one(
            {"call_id": call.call_id},
            {"$setOnInsert": call.model_dump(exclude={"campaign_name"})},
            upsert=True,
        )
    except PyMongoError:
        logger.exception("Database write failed for call %s", call.call_id)
        await asyncio.sleep(1)
        await message.nack(requeue=True)
        return

    await message.ack()


@asynccontextmanager
async def run_consumer(db: AsyncDatabase, settings: Settings):
    async with await aio_pika.connect_robust(
        host=settings.rabbitmq_host,
        login=settings.rabbitmq_user,
        password=settings.rabbitmq_password.get_secret_value(),
    ) as connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        queue = await channel.declare_queue("calls", durable=True)
        await queue.consume(partial(consume, db=db))
        yield
