from fastapi import APIRouter, FastAPI
from importlib.metadata import version
from src.services.communication.message_queue import MessageQueueCommunicationService
from src.external_systems.gateway.rest_api.fast_api_impl.routers.download.video import (
    get_download_video_router,
)


class FastApiGateWay:
    def __init__(
        self, *, message_queue_service: MessageQueueCommunicationService
    ) -> None:
        self.__message_queue_service = message_queue_service
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
        ]

        for router in routers:
            self.__app.include_router(prefix=self.__base_api, router=router)

    def get_app(self) -> FastAPI:
        """getting the api app (FastApi in this case)"""
        return self.__app
