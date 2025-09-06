from dataclasses import dataclass
import os
from dotenv import find_dotenv, load_dotenv


class SqliteDatabaseConfigs:
    @dataclass(frozen=True, slots=True, kw_only=True)
    class Production:
        load_dotenv(dotenv_path=find_dotenv("src/configs/prod.env"), override=True)
        database_path: str = os.getenv("SQLITE_DB_PATH", "")

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Testing:
        load_dotenv(dotenv_path=find_dotenv("src/configs/qa.env"), override=True)
        database_path: str = os.getenv("SQLITE_DB_PATH", "")
