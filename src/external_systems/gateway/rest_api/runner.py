from src.configs.sqlite import SqliteDatabaseConfigs
from src.services.video.youtube import YouTubeVideoService
from src.adapters.outbound.ai.video.youtube.insights_analyzer import (
    YouTubeVideoInsightsAnalyzerAIAgent,
)
from src.configs.ai_agents import AIAgentsConfigs
from src.adapters.outbound.ai.nutrition_breakdown import NutritionBreakdownAIAgent
from src.services.ai import AIService
from src.services.communication.message_queue import MessageQueueCommunicationService
from src.configs.rabbitmq import RabbitMQConfigs
from src.external_systems.gateway.rest_api.fast_api_impl import FastApiGateWay
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_producer import (
    PikaRabbitMqMessageProducer,
)
from src.adapters.outbound.video.youtube.repository.sqlite.pony_impl import (
    SqlitePonyYouTubeVideoRepository,
)
from src.adapters.inbound.video.youtube.downloader.yt_dlp import (
    YtDlpYouTubeVideoDownloader,
)
from src.adapters.inbound.video.youtube.fetcher.yt_dlp import YtDlpYouTubeVideoFetcher
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_consumer import (
    PikaRabbitMqMessageConsumer,
)
import nest_asyncio

nest_asyncio.apply()

# TODO maybe making this dependencies in a better way (Data Class maybe?) 😁

rabbitmq_configs = RabbitMQConfigs.Production()
sqlite_configs = SqliteDatabaseConfigs.Production()

message_producer = PikaRabbitMqMessageProducer(
    rabbitmq_host=rabbitmq_configs.host,
    rabbitmq_port=int(rabbitmq_configs.port),
    rabbitmq_password=rabbitmq_configs.password,
    rabbitmq_username=rabbitmq_configs.username,
)
message_consumer = PikaRabbitMqMessageConsumer(
    rabbitmq_host=rabbitmq_configs.host,
    rabbitmq_port=int(rabbitmq_configs.port),
    rabbitmq_password=rabbitmq_configs.password,
    rabbitmq_username=rabbitmq_configs.username,
)

message_queue_service = MessageQueueCommunicationService(
    message_producer=message_producer, message_consumer=message_consumer
)

ai_agents_configs = AIAgentsConfigs.Production()

ai_service = AIService(
    nutrition_breakdown_ai_agent=NutritionBreakdownAIAgent(
        ollama_base_url=ai_agents_configs.ollama_base_url,
        ollama_model=ai_agents_configs.nutrition_agent_model,
        agent_system_prompt=ai_agents_configs.nutrition_agent_system_prompt,
    ),
    youtube_video_insights_analyzer_ai_agent=YouTubeVideoInsightsAnalyzerAIAgent(
        ollama_base_url=ai_agents_configs.ollama_base_url,
        ollama_model=ai_agents_configs.youtube_analyzer_agent_model,
        agent_system_prompt=ai_agents_configs.youtube_analyzer_agent_system_prompt,
    ),
)

youtube_video_service = YouTubeVideoService(
    youtube_video_downloader=YtDlpYouTubeVideoDownloader(),
    youtube_video_fetcher=YtDlpYouTubeVideoFetcher(),
    youtube_video_repository=SqlitePonyYouTubeVideoRepository(
        database_path=sqlite_configs.database_path
    ),
)


app = FastApiGateWay(
    message_queue_service=message_queue_service,
    ai_service=ai_service,
    youtube_video_service=youtube_video_service,
).get_app()
