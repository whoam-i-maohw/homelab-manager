from pydantic import BaseModel, Field

from src.domain.entity.ai.nutrition_breakdown import NutritionBreakdown


class NutritionBreakdownRequest(BaseModel):
    image_uri: str = Field(
        description="Uri of the image that needs to be analyzed",
        examples=["/tmp/image.jpg"],
        frozen=True,
        kw_only=True,
    )
    initial_prompt: str = Field(
        description="The initial prompt that the AI Agent will be using to get results",
        examples=[
            "this is a dinner of chicken and tomato source called marry me chicken recipe"
        ],
        frozen=True,
        kw_only=True,
    )


class NutritionBreakdownResponse:
    class Success(BaseModel):
        nutrition_breakdown: NutritionBreakdown

    class Error(BaseModel):
        message: str = Field(
            description="Message about the response",
            examples=["Failed to get nutrition ..."],
            frozen=True,
            kw_only=True,
        )
