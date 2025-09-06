from src.domain.entity.error.message_queue import SavingEventError
from src.domain.entity.events.generic import GenericEvent
from src.ports.outbound.event.repository import EventRepositoryInterface


class EventService:
    def __init__(self, *, event_repository: EventRepositoryInterface) -> None:
        self.__event_repository = event_repository

    def save_event(self, *, event: GenericEvent) -> SavingEventError | None:
        return self.__event_repository.save_event(event=event)

    def get_events_by_topic(self, *, topic: str) -> list[GenericEvent]:
        return self.__event_repository.get_events_by_topic(topic=topic)
