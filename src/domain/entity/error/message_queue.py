from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class ProducingMessageError:
    error: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ConsumingMessageError:
    error: str
