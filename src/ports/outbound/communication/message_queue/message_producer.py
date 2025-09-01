from abc import ABC, abstractmethod

from src.domain.entity.error.message_queue import ProducingMessageError


class MessageProducerInterface(ABC):
    @abstractmethod
    def __init__(self) -> None:
        raise Exception("This should be implemented from an adapter !")

    @abstractmethod
    def produce_message(
        self, *, topic: str, data: bytes
    ) -> ProducingMessageError | None:
        """Producing a message to the message queue at this specific topic specified

        Args:
            topic (str): The topic that the message should be delivered to
            data (bytes): The data that should be send as a message [This should be bytes out of json format object]
        """
        raise Exception("This should be implemented from an adapter !")
