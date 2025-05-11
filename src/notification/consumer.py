from aio_pika import IncomingMessage
from src.database.database import rabbit_manager


async def on_message(message: IncomingMessage):
    async with message.process():
        print(f">>>> Received message: {message.body.decode()}")


async def start_consumer():
    channel = await rabbit_manager.get_channel()
    queue = await channel.declare_queue("messages", durable=True)
    await queue.consume(on_message)
