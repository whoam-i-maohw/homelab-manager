from abc import ABC, abstractmethod
from typing import Any, Callable
from src.domain.entity.error.message_queue import ConsumingMessageError


class MessageConsumerInterface(ABC):
    @abstractmethod
    def __init__(self) -> None:
        raise Exception("This should be implemented from an adapter!")

    @abstractmethod
    def consume_messages[T](
        self,
        *,
        exchange_name: str,
        queue_topic: str,
        deserialization_function: Callable[[dict[str, Any]], T],
        callback_function: Callable[[T], Any],
        consume_forever: bool = True,
        retry_attempts: int = 3,
        retry_timeout: int = 3,
    ) -> ConsumingMessageError | None:
        """Consume messages from a specific topic in a message queue

        Args:
            exchange_name (str): The exchange that the messages will be consumed from
            queue_topic (str): The queue topic that the messages will be consumed from
            deserialization_function (Callable[[dict[str, Any]], T]): The deserialization function that will be used
            callback_function (Callable[[T], Any]): Call back function to be called when getting a new message
            consume_forever (bool): If this consumption will run forever or just once. Defaults to True
            retry_attempts (int): The retry attempts number if there is any error. Defaults to 3 attempts
            retry_timeout (int): The retry timeout. Defaults to 3 seconds

        """
        raise Exception("This should be implemented from an adapter!")
