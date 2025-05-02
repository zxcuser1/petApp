from aio_pika import connect_robust, Message
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel


class RabbitMQManager:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractRobustChannel | None = None

    async def connect(self):
        if self._connection is None:
            self._connection = await connect_robust(host=self.host, port=self.port)
            self._channel = await self._connection.channel()

    async def get_channel(self) -> AbstractRobustChannel:
        if self._channel is None:
            await self.connect()
        return self._channel

    async def publish(self, queue_name: str, body: str):
        channel = await self.get_channel()
        await channel.default_exchange.publish(
            Message(body=body.encode()),
            routing_key=queue_name
        )

    async def close(self):
        if self._connection:
            await self._connection.close()
            self._connection = None
            self._channel = None
