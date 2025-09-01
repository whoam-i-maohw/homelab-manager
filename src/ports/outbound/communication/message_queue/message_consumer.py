from abc import ABC, abstractmethod
from typing import Any, Callable, Type
from src.domain.entity.error.message_queue import ConsumingMessageError


class MessageConsumerInterface(ABC):
    @abstractmethod
    def __init__(self) -> None:
        raise Exception("This should be implemented from an adapter!")

    @abstractmethod
    def consume_messages[T](
        self,
        *,
        topic: str,
        deserialization_class: Type[T],
        callback_function: Callable[[T], Any],
        consume_forever: bool = True,
    ) -> ConsumingMessageError | None:
        """Consume messages from a specific topic in a message queue

        Args:
            topic (str): The topic that the messages will be consumed from
            deserialization_class (Type[T]): The deserialization type of the messages consumed
            callback_function (Callable[[T], Any]): Call back function to be called when getting a new message
            consume_forever (bool): If this consumption will run forever or just once. Defaults to True

        """
        raise Exception("This should be implemented from an adapter!")
