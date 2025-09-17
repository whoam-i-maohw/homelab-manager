from abc import ABC, abstractmethod

from src.domain.entity.error.ai import AIAgentRunningError


class GenericAIAgentInterface[T](ABC):
    @abstractmethod
    def __init__(
        self, *, ollama_base_url: str, ollama_model: str, agent_system_prompt: str
    ) -> None:
        raise Exception("This should be implemented from an adapter !")

    @abstractmethod
    def run_agent(self, *, initial_prompt: str, **kwargs) -> AIAgentRunningError | T:
        raise Exception("This should be implemented from an adapter !")
