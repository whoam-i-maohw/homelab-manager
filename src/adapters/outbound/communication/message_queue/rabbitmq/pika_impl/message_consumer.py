import asyncio
import datetime
import pickle
import time
from typing import Any, Callable

from aio_pika import ExchangeType, connect_robust
from src.domain.entity.error.message_queue import ConsumingMessageError
from src.ports.outbound.communication.message_queue.message_consumer import (
    MessageConsumerInterface,
)


class PikaRabbitMqMessageConsumer(MessageConsumerInterface):
    def __init__(
        self,
        *,
        rabbitmq_username: str,
        rabbitmq_password: str,
        rabbitmq_host: str,
        rabbitmq_port: int,
        connection_timeout: int = 5,
    ) -> None:
        self.__rabbitmq_username = rabbitmq_username
        self.__rabbitmq_password = rabbitmq_password
        self.__rabbitmq_host = rabbitmq_host
        self.__rabbitmq_port = rabbitmq_port
        self.__connection_timeout = connection_timeout

    async def __process_consume_messages[T](
        self,
        *,
        exchange_name: str,
        queue_topic: str,
        deserialization_function: Callable[[dict[str, Any]], T],
        callback_function: Callable[[T], Any],
        consume_forever: bool = True,
    ) -> ConsumingMessageError | None:
        try:
            connection = await connect_robust(
                host=self.__rabbitmq_host,
                port=self.__rabbitmq_port,
                login=self.__rabbitmq_username,
                password=self.__rabbitmq_password,
                timeout=self.__connection_timeout,
            )

            async with connection:
                channel = await connection.channel()
                exchange = await channel.declare_exchange(
                    name=exchange_name, type=ExchangeType.FANOUT
                )
                queue = await channel.declare_queue(name=queue_topic, durable=True)
                await queue.bind(exchange)

                print(
                    f" [*] Waiting for messages from [{queue_topic}]. To exit press CTRL+C"
                )

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            callback_function(
                                deserialization_function(pickle.loads(message.body))
                            )
                            if not consume_forever:
                                return None
        except Exception as ex:
            return ConsumingMessageError(error=str(ex))

    def consume_messages[T](
        self,
        *,
        exchange_name: str,
        queue_topic: str,
        deserialization_function: Callable[[dict[str, Any]], T],
        callback_function: Callable[[T], Any],
        consume_forever: bool = True,
        retry_attempts: int = 5,
        retry_timeout: int = 3,
    ) -> ConsumingMessageError | None:
        def __process(*, initial_time: datetime.datetime, initial_retry_attempts: int):
            consumption_status = asyncio.run(
                self.__process_consume_messages(
                    exchange_name=exchange_name,
                    queue_topic=queue_topic,
                    deserialization_function=deserialization_function,
                    callback_function=callback_function,
                    consume_forever=consume_forever,
                )
            )
            current_retry_attempts = retry_attempts
            if isinstance(consumption_status, ConsumingMessageError):
                print(
                    f" [x] Error consuming messages for topic [{queue_topic}] for reason [{consumption_status.error}] ..."
                )
                delta_time = datetime.datetime.now() - initial_time
                if (
                    delta_time.seconds > 60
                ):  # if error is more than 1 min, repeat the retry attempts since it's not circular ;)
                    current_retry_attempts = initial_retry_attempts

                if current_retry_attempts > 0:
                    print(
                        f" [x] Retrying again in [{retry_timeout}] seconds, Remaining attempts [{retry_attempts-1}] ..."
                    )
                    time.sleep(retry_timeout)
                    return self.consume_messages(
                        exchange_name=exchange_name,
                        queue_topic=queue_topic,
                        deserialization_function=deserialization_function,
                        callback_function=callback_function,
                        consume_forever=consume_forever,
                        retry_attempts=retry_attempts - 1,
                        retry_timeout=retry_timeout,
                    )
                else:
                    print(
                        f" [x] Exhausted all retry attempts consuming messages from topic [{queue_topic}] ..."
                    )
                    return consumption_status

        return __process(
            initial_retry_attempts=retry_attempts, initial_time=datetime.datetime.now()
        )
