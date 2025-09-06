from typing import Any, Callable
from src.domain.entity.error.message_queue import (
    ConsumingMessageError,
    ProducingMessageError,
)
from src.ports.outbound.communication.message_queue.message_producer import (
    MessageProducerInterface,
)
from src.ports.outbound.communication.message_queue.message_consumer import (
    MessageConsumerInterface,
)


class MessageQueueCommunicationService:
    def __init__(
        self,
        *,
        message_producer: MessageProducerInterface,
        message_consumer: MessageConsumerInterface,
    ) -> None:
        self.__message_producer = message_producer
        self.__message_consumer = message_consumer

    def produce_message(
        self, *, topic: str, data: bytes
    ) -> ProducingMessageError | None:
        return self.__message_producer.produce_message(topic=topic, data=data)

    def consume_messages[T](
        self,
        *,
        topic: str,
        deserialization_function: Callable[[dict[str, Any]], T],
        callback_function: Callable[[T], Any],
        consume_forever: bool = True,
    ) -> ConsumingMessageError | None:
        return self.__message_consumer.consume_messages(
            topic=topic,
            deserialization_function=deserialization_function,
            callback_function=callback_function,
            consume_forever=consume_forever,
        )
