from typing import Any, Generator
from unittest.mock import Mock, patch
from testcontainer_python_rabbitmq import RabbitMQContainer
from src.domain.entity.error.ai import AIAgentRunningError
from src.domain.entity.ai.nutrition_breakdown import NutritionBreakdown
from src.external_systems.gateway.rest_api.fast_api_impl.models.ai.nutrition_breakdown import (
    NutritionBreakdownRequest,
    NutritionBreakdownResponse,
)
from src.adapters.outbound.ai.nutrition_breakdown import NutritionBreakdownAIAgent
from src.configs.ai_agents import AIAgentsConfigs
from src.services.ai import AIService
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_consumer import (
    PikaRabbitMqMessageConsumer,
)
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_producer import (
    PikaRabbitMqMessageProducer,
)
from src.external_systems.gateway.rest_api.fast_api_impl import FastApiGateWay
from fastapi.testclient import TestClient
from src.services.communication.message_queue import MessageQueueCommunicationService
import pytest
import nest_asyncio
from fastapi import status
from tempfile import mkstemp

nest_asyncio.apply()


@pytest.fixture()
def fastapi_testing_client() -> Generator[TestClient, Any, None]:
    with RabbitMQContainer() as container:
        message_queue_service = MessageQueueCommunicationService(
            message_producer=PikaRabbitMqMessageProducer(
                rabbitmq_host=container.get_container_host_ip(),
                rabbitmq_port=int(container.get_amqp_port()),
                rabbitmq_username="guest",
                rabbitmq_password="guest",
            ),
            message_consumer=PikaRabbitMqMessageConsumer(
                rabbitmq_host=container.get_container_host_ip(),
                rabbitmq_port=int(container.get_amqp_port()),
                rabbitmq_username="guest",
                rabbitmq_password="guest",
            ),
        )

        ai_agents_configs = AIAgentsConfigs.Testing()
        ai_service = AIService(
            nutrition_breakdown_ai_agent=NutritionBreakdownAIAgent(
                agent_system_prompt=ai_agents_configs.nutrition_agent_system_prompt,
                ollama_base_url=ai_agents_configs.ollama_base_url,
                ollama_model=ai_agents_configs.nutrition_agent_model,
            )
        )

        app = FastApiGateWay(
            message_queue_service=message_queue_service, ai_service=ai_service
        ).get_app()
        yield TestClient(app)


@patch(
    "src.services.ai.AIService.get_nutrition_breakdown_from_image",
    return_value=NutritionBreakdown(
        calories="",
        carbohydrates="",
        fats="",
        fiber="",
        protein="",
        saturated_fat="",
        sodium="",
        sugar="",
        summary="",
    ),
)
def test_valid_request_to_get_nutrition_breakdown(
    _mock_socket: Mock,
    fastapi_testing_client: TestClient,
) -> None:
    _file_descriptor, temp_file = mkstemp()
    response = fastapi_testing_client.post(
        "/api/v1/ai/nutrition_breakdown",
        json=NutritionBreakdownRequest(
            image_uri=temp_file, initial_prompt="Initial prompt calling"
        ).model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK

    response_decoding = NutritionBreakdownResponse.Success(**response.json())
    assert response_decoding.nutrition_breakdown == NutritionBreakdown(
        calories="",
        carbohydrates="",
        fats="",
        fiber="",
        protein="",
        saturated_fat="",
        sodium="",
        sugar="",
        summary="",
    )


@patch(
    "src.services.ai.AIService.get_nutrition_breakdown_from_image",
    return_value=AIAgentRunningError(
        error="Error fetching nutrition breakdown from agent",
        initial_prompt="",
        ollama_base_url="",
        ollama_model="",
    ),
)
def test_invalid_fetching_of_nutrition_breakdown(
    _mock_socket: Mock,
    fastapi_testing_client: TestClient,
) -> None:
    _file_descriptor, temp_file = mkstemp()
    response = fastapi_testing_client.post(
        "/api/v1/ai/nutrition_breakdown",
        json=NutritionBreakdownRequest(
            image_uri=temp_file, initial_prompt="Initial prompt calling"
        ).model_dump(),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response_decoding = NutritionBreakdownResponse.Error(**response.json())
    assert (
        response_decoding.message
        == "Error fetching nutrition breakdown for the reason [Error fetching nutrition breakdown from agent] ..."
    )
