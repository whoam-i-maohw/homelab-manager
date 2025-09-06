import datetime
from typing import Any, Generator
import pytest

from src.domain.entity.error.message_queue import (
    GenericEvent,
    SavingEventError,
)
from src.domain.entity.events.generic import GenericEvent
from src.adapters.outbound.event.repository.sqlite.pony_impl import (
    PonySqliteEventRepository,
)


@pytest.fixture
def setup_db() -> Generator[PonySqliteEventRepository, Any, None]:
    yield PonySqliteEventRepository(database_path=":memory:")


def get_dummy_event() -> GenericEvent:
    return GenericEvent(created_at_iso_format=datetime.datetime.now().isoformat())


def test_save_event(setup_db: PonySqliteEventRepository) -> None:
    db = setup_db
    event = get_dummy_event()
    save_event_status = db.save_event(event=event)

    assert save_event_status is None


def test_save_same_event_twice(setup_db: PonySqliteEventRepository) -> None:
    db = setup_db
    event = get_dummy_event()
    save_event_status = db.save_event(event=event)

    assert save_event_status is None

    save_event_status = db.save_event(event=event)

    assert isinstance(save_event_status, SavingEventError)
    assert save_event_status.error == "This event is already existed in the database !"
    assert save_event_status.event == event


def test_get_events_for_topic(setup_db: PonySqliteEventRepository) -> None:
    db = setup_db
    event = get_dummy_event()

    save_event_status = db.save_event(event=event)

    assert save_event_status is None

    getting_events_status = db.get_events_by_topic(topic=event.get_topic())
    assert len(getting_events_status) == 1
    assert getting_events_status[0] == event


def test_get_events_for_non_existing_topic(
    setup_db: PonySqliteEventRepository,
) -> None:
    db = setup_db

    getting_events_status = db.get_events_by_topic(topic="non-existence")
    assert len(getting_events_status) == 0
    assert getting_events_status == []
