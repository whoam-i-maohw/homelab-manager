from dataclasses import dataclass
import os

from dotenv import find_dotenv, load_dotenv


class AIAgentsConfigs:
    @dataclass(frozen=True, slots=True, kw_only=True)
    class Production:
        load_dotenv(dotenv_path=find_dotenv("src/configs/prod.env"), override=True)
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "")
        nutrition_agent_model = os.getenv("OLLAMA_NUTRITION_AGENT_MODEL", "")
        nutrition_agent_system_prompt = os.getenv("NUTRITION_AGENT_SYSTEM_PROMPT", "")

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Testing:
        load_dotenv(dotenv_path=find_dotenv("src/configs/qa.env"), override=True)
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "")
        nutrition_agent_model = os.getenv("OLLAMA_NUTRITION_AGENT_MODEL", "")
        nutrition_agent_system_prompt = os.getenv("NUTRITION_AGENT_SYSTEM_PROMPT", "")
