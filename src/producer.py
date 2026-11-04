import asyncio
import json

import aio_pika

from config import Settings


async def main() -> None:
    settings = Settings()
    campaigns = [
        ("camp_001", "Notification about payment"),
        ("camp_002", "Confirmation of record"),
    ]

    async with await aio_pika.connect_robust(
        host=settings.rabbitmq_host,
        login=settings.rabbitmq_user,
        password=settings.rabbitmq_password.get_secret_value(),
    ) as connection:
        channel = await connection.channel(publisher_confirms=True)
        await channel.declare_queue("calls", durable=True)

        for campaign_number, (campaign_id, name) in enumerate(campaigns):
            for call_number in range(2):
                number = campaign_number * 2 + call_number + 1
                call = {
                    "call_id": f"call_{number:04d}",
                    "campaign_id": campaign_id,
                    "campaign_name": name,
                    "phone": f"790012345{number:02d}",
                    "status": "success",
                    "created_at": "2026-10-20T10:06:00Z",
                }
                await channel.default_exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(call, ensure_ascii=False).encode(),
                        content_type="application/json",
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    ),
                    routing_key="calls",
                )

    print("Published 4 messages: 2 per campaign.")


if __name__ == "__main__":
    asyncio.run(main())
