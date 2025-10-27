from fastapi import APIRouter, FastAPI
from importlib.metadata import version

from fastapi_mcp import FastApiMCP
from src.services.video.youtube import YouTubeVideoService
from src.external_systems.gateway.rest_api.fast_api_impl.routers.ai.youtube_analyzer import (
    get_youtube_analyzer_router,
)
from src.services.ai import AIService
from src.external_systems.gateway.rest_api.fast_api_impl.routers.ai.nutrition_breakdown import (
    get_nutrition_breakdown_router,
)
from src.services.communication.message_queue import MessageQueueCommunicationService
from src.external_systems.gateway.rest_api.fast_api_impl.routers.download.video import (
    get_download_video_router,
)


class FastApiGateWay:
    def __init__(
        self,
        *,
        message_queue_service: MessageQueueCommunicationService,
        youtube_video_service: YouTubeVideoService,
        ai_service: AIService,
    ) -> None:
        self.__message_queue_service = message_queue_service
        self.__youtube_video_service = youtube_video_service
        self.__ai_service = ai_service
        self.__current_api_version: int = 1
        self.__base_api: str = f"/api/v{self.__current_api_version}"
        self.__app: FastAPI = FastAPI(
            title="Home Lab Manager Gateway",
            version=version("homelab-manager"),
            description="This project should be the gateway between the client (browser, mobile, etc)"
            + "and the backend services that will be called to do some commands or get some queries",
        )
        routers: list[APIRouter] = [
            get_download_video_router(
                message_queue_service=self.__message_queue_service
            ),
            get_nutrition_breakdown_router(ai_service=self.__ai_service),
            get_youtube_analyzer_router(
                ai_service=self.__ai_service,
                youtube_video_service=self.__youtube_video_service,
            ),
        ]

        for router in routers:
            self.__app.include_router(prefix=self.__base_api, router=router)

        mcp = FastApiMCP(
            self.__app,
            include_operations=[
                "download_youtube_video_from_url_to_channel_name_dir",
                "download_youtube_videos_from_txt_file_to_channel_name_dir",
                "get_nutrition_breakdown_from_image",
                "get_youtube_video_analysis_from_url",
            ],
            describe_all_responses=True,
            describe_full_response_schema=True,
            description="Homelab Manager MCP Server",
        )
        mcp.mount_http()

    def get_app(self) -> FastAPI:
        """getting the api app (FastApi in this case)"""
        return self.__app
