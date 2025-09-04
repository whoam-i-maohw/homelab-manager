import datetime
import pickle
from fastapi import APIRouter, Response, status
from dataclasses import asdict
from src.domain.entity.commands.video.youtube.download_youtube_videos_from_txt_file_command import (
    DownloadYouTubeVideoFromTxtFileCommand,
)
from src.domain.entity.commands.video.youtube.download_youtube_videos_from_txt_file_to_channel_name_dir_command import (
    DownloadYouTubeVideoFromTxtFileToChannelNameDirCommand,
)
from src.domain.entity.commands.video.youtube.download_youtube_video_from_url_to_channel_name_dir_command import (
    DownloadYouTubeVideoFromUrlToChannelNameDirCommand,
)
from src.domain.entity.error.message_queue import ProducingMessageError
from src.domain.entity.commands.video.youtube.download_youtube_video_from_url_command import (
    DownloadYouTubeVideoFromUrlCommand,
)
from src.services.communication.message_queue import MessageQueueCommunicationService

from src.external_systems.gateway.rest_api.fast_api_impl.models.download.video.youtube import (
    DownloadVideoRequest,
    DownloadVideoResponse,
)
from src.domain.entity.commands.generic_command import GenericCommand


def get_download_video_router(
    *,
    message_queue_service: MessageQueueCommunicationService,
) -> APIRouter:
    download_video_router: APIRouter = APIRouter(
        prefix="/download/video",
        tags=["Download Video"],
        include_in_schema=True,
    )

    def __process_message(
        message: GenericCommand, response: Response
    ) -> DownloadVideoResponse.Error | DownloadVideoResponse.Success:
        message_producing_status = message_queue_service.produce_message(
            topic=message.get_topic(), data=pickle.dumps(asdict(message))
        )
        match message_producing_status:
            case ProducingMessageError() as error:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return DownloadVideoResponse.Error(
                    message=f"Failed to request a download for your video [{message}] for reason [{error.error}]"
                )
            case _:
                response.status_code = status.HTTP_200_OK
                print(f" [x] Published message to topic [{message.get_topic()}] ...")
                return DownloadVideoResponse.Success(
                    message="Successfully requested to download this video ...",
                )

    @download_video_router.post(
        "/youtube/to_root_dir",
        description="Request to download a youtube video using a url and save it directly inside a dir path",
        operation_id="download_youtube_video_from_url",
        responses={
            400: {"model": DownloadVideoResponse.Error},
            200: {"model": DownloadVideoResponse.Success},
        },
        response_model=DownloadVideoResponse.Error | DownloadVideoResponse.Success,
    )
    async def download_youtube_video_from_url(
        request: DownloadVideoRequest.FromUrl, response: Response
    ) -> DownloadVideoResponse.Error | DownloadVideoResponse.Success:
        message = DownloadYouTubeVideoFromUrlCommand(
            created_at_iso_format=datetime.datetime.now().isoformat(),
            url=request.url,
            resolution=request.resolution,
            desired_download_path=request.desired_download_path,
        )
        return __process_message(message=message, response=response)

    @download_video_router.post(
        "/youtube/to_channel_name_dir",
        description="Request to download a youtube video using a url and save it directly inside"
        + " a dir path and inside the channel_name directory of the youtube video",
        operation_id="download_youtube_video_from_url_to_channel_name_dir",
        responses={
            400: {"model": DownloadVideoResponse.Error},
            200: {"model": DownloadVideoResponse.Success},
        },
        response_model=DownloadVideoResponse.Error | DownloadVideoResponse.Success,
    )
    async def download_youtube_video_from_url_to_channel_name_dir(
        request: DownloadVideoRequest.FromUrl, response: Response
    ) -> DownloadVideoResponse.Error | DownloadVideoResponse.Success:
        message = DownloadYouTubeVideoFromUrlToChannelNameDirCommand(
            created_at_iso_format=datetime.datetime.now().isoformat(),
            url=request.url,
            resolution=request.resolution,
            desired_download_path=request.desired_download_path,
        )
        return __process_message(message=message, response=response)

    @download_video_router.post(
        "/youtube/from_txt_file_to_root_dir",
        description="Request to download a youtube video using a url and save it directly inside a dir path",
        operation_id="download_youtube_videos_from_txt_file",
        responses={
            400: {"model": DownloadVideoResponse.Error},
            200: {"model": DownloadVideoResponse.Success},
        },
        response_model=DownloadVideoResponse.Error | DownloadVideoResponse.Success,
    )
    async def download_youtube_videos_from_txt_file(
        request: DownloadVideoRequest.FromTxtFile, response: Response
    ) -> DownloadVideoResponse.Error | DownloadVideoResponse.Success:
        message = DownloadYouTubeVideoFromTxtFileCommand(
            created_at_iso_format=datetime.datetime.now().isoformat(),
            txt_file_path=request.txt_file_path,
            resolution=request.resolution,
            desired_download_path=request.desired_download_path,
        )
        return __process_message(message=message, response=response)

    @download_video_router.post(
        "/youtube/from_txt_file_to_channel_name_dir",
        description="Request to download a youtube video using a url and save it directly inside"
        + " a dir path and inside the channel_name directory of the youtube video",
        operation_id="download_youtube_videos_from_txt_file_to_channel_name_dir",
        responses={
            400: {"model": DownloadVideoResponse.Error},
            200: {"model": DownloadVideoResponse.Success},
        },
        response_model=DownloadVideoResponse.Error | DownloadVideoResponse.Success,
    )
    async def download_youtube_videos_from_txt_file_to_channel_name_dir(
        request: DownloadVideoRequest.FromTxtFile, response: Response
    ) -> DownloadVideoResponse.Error | DownloadVideoResponse.Success:
        message = DownloadYouTubeVideoFromTxtFileToChannelNameDirCommand(
            created_at_iso_format=datetime.datetime.now().isoformat(),
            txt_file_path=request.txt_file_path,
            resolution=request.resolution,
            desired_download_path=request.desired_download_path,
        )
        return __process_message(message=message, response=response)

    return download_video_router
