from abc import ABC, abstractmethod

from src.domain.entity.error.message_queue import SavingEventError
from src.domain.entity.events.generic import GenericEvent


class EventRepositoryInterface(ABC):
    @abstractmethod
    def __init__(self) -> None:
        raise Exception("This should be implemented from an adapter !")

    @abstractmethod
    def save_event(self, *, event: GenericEvent) -> SavingEventError | None:
        """Saving a command into a repository/storage

        Args:
            command (GenericCommand): The command that needs to be saved

        Returns:
            SavingCommandError | None: Either an error if there is an error or None if success
        """
        raise Exception("This should be implemented from an adapter !")

    @abstractmethod
    def get_events_by_topic(self, *, topic: str) -> list[GenericEvent]:
        """Getting event(s) by a specific topic

        Args:
            topic (str): The topic that needs all events for

        Returns:
            list[GenericEvent]: list of the events found for a topic
        """
        raise Exception("This should be implemented from an adapter !")
