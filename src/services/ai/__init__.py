from src.domain.entity.ai.youtube import YouTubeVideoInsightsAnalysis
from src.adapters.outbound.ai.video.youtube.insights_analyzer import (
    YouTubeVideoInsightsAnalyzerAIAgent,
)
from src.adapters.outbound.ai.nutrition_breakdown import NutritionBreakdownAIAgent
from src.domain.entity.error.ai import AIAgentRunningError
from src.domain.entity.ai.nutrition_breakdown import NutritionBreakdown


class AIService:
    def __init__(
        self,
        *,
        nutrition_breakdown_ai_agent: NutritionBreakdownAIAgent,
        youtube_video_insights_analyzer_ai_agent: YouTubeVideoInsightsAnalyzerAIAgent,
    ) -> None:
        self.__nutrition_breakdown_ai_agent = nutrition_breakdown_ai_agent
        self.__youtube_video_insights_analyzer_ai_agent = (
            youtube_video_insights_analyzer_ai_agent
        )

    def get_nutrition_breakdown_from_image(
        self, *, image_uri: str, initial_prompt: str, response_in_json: bool = True
    ) -> AIAgentRunningError | str | NutritionBreakdown:
        return self.__nutrition_breakdown_ai_agent.run_agent(
            initial_prompt=initial_prompt,
            image_uri=image_uri,
            response_in_json=response_in_json,
        )

    def get_insights_analysis_from_youtube_video_subtitle(
        self,
        *,
        initial_prompt: str,
        video_subtitle_txt: str,
        response_in_json: bool = True,
    ) -> AIAgentRunningError | str | YouTubeVideoInsightsAnalysis:
        return self.__youtube_video_insights_analyzer_ai_agent.run_agent(
            initial_prompt=initial_prompt,
            video_subtitle_txt=video_subtitle_txt,
            response_in_json=response_in_json,
        )
