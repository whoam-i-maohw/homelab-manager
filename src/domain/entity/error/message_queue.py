from dataclasses import dataclass

from src.domain.entity.events.generic import GenericEvent
from src.domain.entity.commands.generic_command import GenericCommand


@dataclass(frozen=True, slots=True, kw_only=True)
class ProducingMessageError:
    error: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ConsumingMessageError:
    error: str


@dataclass(frozen=True, slots=True, kw_only=True)
class SavingCommandError:
    error: str
    command: GenericCommand


@dataclass(frozen=True, slots=True, kw_only=True)
class SavingEventError:
    error: str
    event: GenericEvent
