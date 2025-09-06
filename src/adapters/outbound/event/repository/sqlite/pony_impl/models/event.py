from pony.orm import Database, Json, PrimaryKey, Required


def register_event_model(*, db: Database):
    class EventModel(db.Entity):
        _table_ = "events"
        topic = Required(str)
        created_at_iso_format = Required(str)
        event_data_class_name = Required(str)
        event_data_json = Required(Json)

        PrimaryKey(topic, created_at_iso_format, event_data_class_name)

    return EventModel
