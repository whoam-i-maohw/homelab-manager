from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class GenericEvent:
    created_at_iso_format: str

    @classmethod
    def get_topic(cls) -> str:
        return cls.__name__
