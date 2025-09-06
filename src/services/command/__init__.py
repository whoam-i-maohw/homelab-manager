from src.domain.entity.error.message_queue import SavingCommandError
from src.domain.entity.commands.generic_command import GenericCommand
from src.ports.outbound.command.repository import CommandRepositoryInterface


class CommandService:
    def __init__(self, *, command_repository: CommandRepositoryInterface) -> None:
        self.__command_repository = command_repository

    def save_command(self, *, command: GenericCommand) -> SavingCommandError | None:
        return self.__command_repository.save_command(command=command)

    def get_commands_by_topic(self, *, topic: str) -> list[GenericCommand]:
        return self.__command_repository.get_commands_by_topic(topic=topic)
