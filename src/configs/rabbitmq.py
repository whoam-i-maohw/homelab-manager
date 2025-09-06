from dataclasses import dataclass
import os
from dotenv import find_dotenv, load_dotenv


class RabbitMQConfigs:
    @dataclass(frozen=True, slots=True, kw_only=True)
    class Production:
        load_dotenv(dotenv_path=find_dotenv("src/configs/prod.env"), override=True)
        host: str = os.getenv("RABBITMQ_HOST", "")
        port: str = os.getenv("RABBITMQ_PORT", "")
        username: str = os.getenv("RABBITMQ_USERNAME", "")
        password: str = os.getenv("RABBITMQ_PASSWORD", "")

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Testing:
        load_dotenv(dotenv_path=find_dotenv("src/configs/qa.env"), override=True)
        host: str = os.getenv("RABBITMQ_HOST", "")
        port: str = os.getenv("RABBITMQ_PORT", "")
        username: str = os.getenv("RABBITMQ_USERNAME", "")
        password: str = os.getenv("RABBITMQ_PASSWORD", "")
