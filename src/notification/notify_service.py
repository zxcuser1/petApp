import asyncio

from pika import ConnectionParameters, BlockingConnection
from aio_pika import connect
from src.database.database import session_factory
from src.database.models import User
from src.database.repository import AsyncBaseRepository
import os

HOST = os.getenv("RABBIT_MQ_HOST")
PORT = os.getenv("RABBIT_MQ_PORT")

CONN_PARAMS = ConnectionParameters(
    host=HOST,
    port=PORT
)


async def notify(user_id: int):
    try:
        with session_factory() as session:
            repo = AsyncBaseRepository(session)
            user = await repo.get_by_id(User, user_id)
            queue = "messages"
            with BlockingConnection() as conn:
                with conn.channel() as ch:
                    ch.queue_declare(queue=queue)
                    ch.basic_publish(
                        exchange="",
                        routing_key=queue,
                        body=f"Notification for {user.Name}. Some one liked you!!"
                    )
            print("Message sent")
    except Exception as ex:
        raise ex


async def read_message(loop):
    queue_name = "messages"
    connection = await connect(host=HOST, port=int(PORT), loop=loop)

    channel = await connection.channel()

    exchange = await channel.declare_exchange('direct')

    queue = await channel.declare_queue(queue_name)

    await queue.bind(exchange, queue_name)

    incoming_message = await queue.get(timeout=5)

    print(f"message: {incoming_message}")

    incoming_message.ack()

    await queue.unbind(exchange, queue_name)
    await queue.delete()
    await connection.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(read_message(loop))