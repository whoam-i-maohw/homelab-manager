from fastapi import APIRouter, Response, status
from src.domain.entity.error.video import GettingYouTubeVideoSubtitleError
from src.domain.entity.video.youtube import YouTubeVideoSubtitle
from src.services.video.youtube import YouTubeVideoService
from src.external_systems.gateway.rest_api.fast_api_impl.models.ai.youtube_video_analysis import (
    YouTubeVideoAnalysisRequest,
    YouTubeVideoAnalysisResponse,
)
from src.domain.entity.ai.youtube import YouTubeVideoInsightsAnalysis
from src.domain.entity.error.ai import AIAgentRunningError
from src.services.ai import AIService


def get_youtube_analyzer_router(
    *, ai_service: AIService, youtube_video_service: YouTubeVideoService
) -> APIRouter:
    youtube_analyzer_router: APIRouter = APIRouter(
        prefix="/ai/youtube_video_analyzer",
        tags=["YouTube Video Analyzer"],
        include_in_schema=True,
    )

    @youtube_analyzer_router.post(
        "/",
        description="Get a youtube video's analysis",
        operation_id="get_youtube_video_analysis_from_url",
        responses={
            400: {"model": YouTubeVideoAnalysisResponse.Error},
            200: {"model": YouTubeVideoAnalysisResponse.Success},
        },
        response_model=YouTubeVideoAnalysisResponse.Error
        | YouTubeVideoAnalysisResponse.Success,
    )
    async def get_youtube_video_analysis_from_url(
        request: YouTubeVideoAnalysisRequest, response: Response
    ) -> YouTubeVideoAnalysisResponse.Error | YouTubeVideoAnalysisResponse.Success:
        getting_youtube_video_transcription_status: (
            GettingYouTubeVideoSubtitleError | YouTubeVideoSubtitle
        ) = youtube_video_service.get_youtube_video_transcription_for_url(
            video_url=request.video_url
        )
        if isinstance(getting_youtube_video_transcription_status, YouTubeVideoSubtitle):
            getting_youtube_video_analysis_status: (
                AIAgentRunningError | str | YouTubeVideoInsightsAnalysis
            ) = ai_service.get_insights_analysis_from_youtube_video_subtitle(
                video_subtitle_txt=getting_youtube_video_transcription_status.subtitle_txt,
                initial_prompt="This is a youtube video's transcription file",
            )
            if isinstance(getting_youtube_video_analysis_status, AIAgentRunningError):
                response.status_code = status.HTTP_400_BAD_REQUEST
                return YouTubeVideoAnalysisResponse.Error(
                    message=(
                        f"Error fetching youtube video's analysis for the reason"
                        f"[{getting_youtube_video_analysis_status.error}] ..."
                    )
                )
            elif isinstance(
                getting_youtube_video_analysis_status, YouTubeVideoInsightsAnalysis
            ):
                response.status_code = status.HTTP_200_OK
                return YouTubeVideoAnalysisResponse.Success(
                    youtube_video_analysis=getting_youtube_video_analysis_status
                )
            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return YouTubeVideoAnalysisResponse.Error(
                    message="Error getting the youtube video's analysis as Json !"
                )
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return YouTubeVideoAnalysisResponse.Error(
                message=(
                    "Error getting the youtube video's analysis as Json "
                    f"for the reason [{getting_youtube_video_transcription_status.error}] ..."
                )
            )

    return youtube_analyzer_router
