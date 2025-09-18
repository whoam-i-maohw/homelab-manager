from src.adapters.outbound.ai.nutrition_breakdown import NutritionBreakdownAIAgent
from src.domain.entity.error.ai import AIAgentRunningError
from src.domain.entity.ai.nutrition_breakdown import NutritionBreakdown


class AIService:
    def __init__(
        self, *, nutrition_breakdown_ai_agent: NutritionBreakdownAIAgent
    ) -> None:
        self.__nutrition_breakdown_ai_agent = nutrition_breakdown_ai_agent

    def get_nutrition_breakdown_from_image(
        self, *, image_uri: str, initial_prompt: str, response_in_json: bool = True
    ) -> AIAgentRunningError | str | NutritionBreakdown:
        return self.__nutrition_breakdown_ai_agent.run_agent(
            initial_prompt=initial_prompt,
            image_uri=image_uri,
            response_in_json=response_in_json,
        )
