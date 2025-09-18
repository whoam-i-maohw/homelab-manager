from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AIAgentRunningError:
    error: str
    initial_prompt: str
    ollama_base_url: str
    ollama_model: str
