from pydantic import BaseModel, Field


class DownloadVideoRequest:
    class FromUrl(BaseModel):
        url: str = Field(
            description="Url of the video to be downloaded",
            examples=["https://www.youtube.com/watch?v=video-uuid"],
            frozen=True,
            kw_only=True,
        )
        resolution: int = Field(
            default=1080,
            description="The resolution of the video to be downloaded as",
            examples=[1080, 720, 360],
            frozen=True,
            kw_only=True,
        )
        desired_download_path: str = Field(
            description="The path that the video will be downloaded on the server",
            examples=["/tmp"],
            frozen=True,
            kw_only=True,
        )

    class FromTxtFile(BaseModel):
        txt_file_path: str = Field(
            description="The txt file path that has url(s) of the videos to be downloaded",
            examples=["/tmp/urls.txt"],
            frozen=True,
            kw_only=True,
        )
        resolution: int = Field(
            default=1080,
            description="The resolution of the video(s) to be downloaded as",
            examples=[1080, 720, 360],
            frozen=True,
            kw_only=True,
        )
        desired_download_path: str = Field(
            description="The path that the video(s) will be downloaded on the server",
            examples=["/tmp"],
            frozen=True,
            kw_only=True,
        )


class DownloadVideoResponse:
    class Success(BaseModel):
        message: str = Field(
            description="Message about the response",
            examples=["Successfully requested abc ..."],
            frozen=True,
            kw_only=True,
        )

    class Error(BaseModel):
        message: str = Field(
            description="Message about the response",
            examples=["Failed to request abc ..."],
            frozen=True,
            kw_only=True,
        )
