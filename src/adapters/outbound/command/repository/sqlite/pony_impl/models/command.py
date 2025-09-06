from pony.orm import Database, Json, PrimaryKey, Required


def register_command_model(*, db: Database):
    class CommandModel(db.Entity):
        _table_ = "commands"
        topic = Required(str)
        created_at_iso_format = Required(str)
        command_data_class_name = Required(str)
        command_data_json = Required(Json)

        PrimaryKey(topic, created_at_iso_format, command_data_class_name)

    return CommandModel
