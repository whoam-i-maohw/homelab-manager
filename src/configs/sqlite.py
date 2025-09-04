from dataclasses import dataclass
import os
from dotenv import find_dotenv, load_dotenv


class SqliteDatabaseConfigs:
    @dataclass(frozen=True, slots=True, kw_only=True)
    class Production:
        load_dotenv(dotenv_path=find_dotenv("prod.env"))
        database_path: str = os.getenv("SQLITE_DB_PATH", "")
