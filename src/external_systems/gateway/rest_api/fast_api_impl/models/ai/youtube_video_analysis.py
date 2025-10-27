from pydantic import BaseModel, Field

from src.domain.entity.ai.youtube import YouTubeVideoInsightsAnalysis


class YouTubeVideoAnalysisRequest(BaseModel):
    video_url: str = Field(
        description="The youtube video's url",
        examples=["https://www.youtube.com/shorts/VIDEO_UUID"],
        frozen=True,
        kw_only=True,
    )


class YouTubeVideoAnalysisResponse:
    class Success(BaseModel):
        youtube_video_analysis: YouTubeVideoInsightsAnalysis

    class Error(BaseModel):
        message: str = Field(
            description="Message about the response",
            examples=["Failed to get nutrition ..."],
            frozen=True,
            kw_only=True,
        )
