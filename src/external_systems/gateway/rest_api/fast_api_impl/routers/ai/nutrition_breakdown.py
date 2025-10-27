from fastapi import APIRouter, Response, status
from src.domain.entity.ai.nutrition_breakdown import NutritionBreakdown
from src.domain.entity.error.ai import AIAgentRunningError
from src.external_systems.gateway.rest_api.fast_api_impl.models.ai.nutrition_breakdown import (
    NutritionBreakdownRequest,
    NutritionBreakdownResponse,
)
from src.services.ai import AIService


def get_nutrition_breakdown_router(
    *,
    ai_service: AIService,
) -> APIRouter:
    nutrition_breakdown_router: APIRouter = APIRouter(
        prefix="/ai/nutrition_breakdown",
        tags=["Nutrition Breakdown"],
        include_in_schema=True,
    )

    @nutrition_breakdown_router.post(
        "/",
        description="Get nutrition breakdown from an image",
        operation_id="get_nutrition_breakdown_from_image",
        responses={
            400: {"model": NutritionBreakdownResponse.Error},
            200: {"model": NutritionBreakdownResponse.Success},
        },
        response_model=NutritionBreakdownResponse.Error
        | NutritionBreakdownResponse.Success,
    )
    async def get_nutrition_breakdown_from_image(
        request: NutritionBreakdownRequest, response: Response
    ) -> NutritionBreakdownResponse.Error | NutritionBreakdownResponse.Success:
        getting_nutrition_breakdown_status: (
            AIAgentRunningError | str | NutritionBreakdown
        ) = ai_service.get_nutrition_breakdown_from_image(
            image_uri=request.image_uri, initial_prompt=request.initial_prompt
        )
        match getting_nutrition_breakdown_status:
            case AIAgentRunningError() as error:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return NutritionBreakdownResponse.Error(
                    message=f"Error fetching nutrition breakdown for the reason [{error.error}] ..."
                )
            case NutritionBreakdown() as nutrition_breakdown:
                response.status_code = status.HTTP_200_OK
                return NutritionBreakdownResponse.Success(
                    nutrition_breakdown=nutrition_breakdown
                )
            case _:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return NutritionBreakdownResponse.Error(
                    message="Error getting the nutrition breakdown as Json !"
                )

    return nutrition_breakdown_router
