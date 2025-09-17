from unittest.mock import Mock, patch
from src.domain.entity.ai.nutrition_breakdown import NutritionBreakdown
from src.domain.entity.error.ai import AIAgentRunningError
from src.adapters.outbound.ai.nutrition_breakdown import NutritionBreakdownAIAgent
from src.configs.ai_agents import AIAgentsConfigs
from dataclasses import asdict, dataclass
from tempfile import mkstemp


@dataclass(frozen=True, slots=True, kw_only=True)
class CustomAgentSyncRunResponse:
    output = """```json
    {
        "summary" : "",
        "calories" : "",
        "carbohydrates" : "",
        "fats" : "",
        "fiber" : "",
        "protein" : "",
        "saturated_fat" : "",
        "sodium" : "",
        "sugar" : ""
    }
```"""


@patch(
    "src.adapters.outbound.ai.nutrition_breakdown.Agent.run_sync",
    return_value=CustomAgentSyncRunResponse(),
)
def test_happy_path(_mock_socket: Mock) -> None:
    expected_status = NutritionBreakdown(
        summary="",
        calories="",
        carbohydrates="",
        fats="",
        fiber="",
        protein="",
        saturated_fat="",
        sodium="",
        sugar="",
    )

    _file_descriptor, temp_file = mkstemp()

    ai_agents_configs = AIAgentsConfigs.Testing()
    running_agent_status: AIAgentRunningError | NutritionBreakdown = (
        NutritionBreakdownAIAgent(
            ollama_base_url=ai_agents_configs.ollama_base_url,
            ollama_model=ai_agents_configs.nutrition_agent_model,
            agent_system_prompt=ai_agents_configs.nutrition_agent_system_prompt,
        ).run_agent(initial_prompt="Testing prompt", image_uri=temp_file)
    )

    assert isinstance(running_agent_status, NutritionBreakdown)
    assert running_agent_status == expected_status


@patch(
    "src.adapters.outbound.ai.nutrition_breakdown.Agent.run_sync",
    side_effect=Exception("Error fetching nutrition from agent"),
)
def test_error_fetching_nutrition_breakdown_from_nutrition_agent(
    _mock_socket: Mock,
) -> None:
    initial_prompt: str = "Testing prompt"
    _file_descriptor, temp_file = mkstemp()

    ai_agents_configs = AIAgentsConfigs.Testing()
    running_agent_status: AIAgentRunningError | NutritionBreakdown = (
        NutritionBreakdownAIAgent(
            ollama_base_url=ai_agents_configs.ollama_base_url,
            ollama_model=ai_agents_configs.nutrition_agent_model,
            agent_system_prompt=ai_agents_configs.nutrition_agent_system_prompt,
        ).run_agent(initial_prompt=initial_prompt, image_uri=temp_file)
    )

    expected_status = AIAgentRunningError(
        error="Error fetching nutrition from agent",
        initial_prompt=initial_prompt,
        ollama_base_url=ai_agents_configs.ollama_base_url,
        ollama_model=ai_agents_configs.nutrition_agent_model,
    )

    assert isinstance(running_agent_status, AIAgentRunningError)
    assert running_agent_status == expected_status
