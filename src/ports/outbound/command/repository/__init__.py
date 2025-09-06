from abc import ABC, abstractmethod

from src.domain.entity.error.message_queue import SavingCommandError
from src.domain.entity.commands.generic_command import GenericCommand


class CommandRepositoryInterface(ABC):
    @abstractmethod
    def __init__(self) -> None:
        raise Exception("This should be implemented from an adapter !")

    @abstractmethod
    def save_command(self, *, command: GenericCommand) -> SavingCommandError | None:
        """Saving a command into a repository/storage

        Args:
            command (GenericCommand): The command that needs to be saved

        Returns:
            SavingCommandError | None: Either an error if there is an error or None if success
        """
        raise Exception("This should be implemented from an adapter !")

    @abstractmethod
    def get_commands_by_topic(self, *, topic: str) -> list[GenericCommand]:
        """Getting command by a specific topic

        Args:
            topic (str): The topic that needs all commands for

        Returns:
            list[GenericCommand]: list of the commands found for a topic
        """
        raise Exception("This should be implemented from an adapter !")
