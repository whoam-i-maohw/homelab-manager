import os
import sys
import time
from types import CoroutineType
from typing import Any, Callable
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes,
)
import nest_asyncio

from src.adapters.outbound.ai.video.youtube.insights_analyzer import (
    YouTubeVideoInsightsAnalyzerAIAgent,
)
from src.adapters.outbound.ai.nutrition_breakdown import NutritionBreakdownAIAgent
from src.configs.ai_agents import AIAgentsConfigs
from src.services.ai import AIService

nest_asyncio.apply()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.message is not None
    await update.message.reply_text("Send me an image!")


def __handle_photo__wrapper(
    *, ai_service: AIService
) -> Callable[..., CoroutineType[Any, Any, None]]:
    async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = update.message
        assert message is not None

        initial_prompt = message.caption or "This is my dinner today"

        assert update.message is not None
        photo = update.message.photo[-1]  # Get the highest resolution photo
        file = await context.bot.get_file(photo.file_id)

        assert file.file_path is not None
        await update.message.reply_text(
            f"""
            This is the nutrition breakdown:
            {ai_service.get_nutrition_breakdown_from_image(
                image_uri=file.file_path,
                initial_prompt=initial_prompt,
                response_in_json=False)}
            """
        )

    return handle_photo


def main() -> None:
    ai_agents_configs = AIAgentsConfigs.Production()
    ai_service = AIService(
        nutrition_breakdown_ai_agent=NutritionBreakdownAIAgent(
            ollama_model=ai_agents_configs.nutrition_agent_model,
            ollama_base_url=ai_agents_configs.ollama_base_url,
            agent_system_prompt=ai_agents_configs.nutrition_agent_system_prompt,
        ),
        youtube_video_insights_analyzer_ai_agent=YouTubeVideoInsightsAnalyzerAIAgent(
            ollama_base_url=ai_agents_configs.ollama_base_url,
            ollama_model=ai_agents_configs.youtube_analyzer_agent_model,
            agent_system_prompt=ai_agents_configs.youtube_analyzer_agent_system_prompt,
        ),
    )

    app = (
        ApplicationBuilder()
        .token(ai_agents_configs.telegram_nutrition_breakdown_bot_token)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.PHOTO, __handle_photo__wrapper(ai_service=ai_service))
    )

    print(" [x] Telegram NutritionBreakdown Chat Bot Running And Polling Messages ...")
    app.run_polling()


def entry(*, retry_attempts: int = 3, retry_timeout: int = 3) -> None:
    if retry_attempts > 0:
        try:
            return main()
        except Exception as ex:
            print(f" [x] Error running the event handler for reason: [{str(ex)}] ...")
            print(
                f" [x] Retrying again in [{retry_timeout}] seconds, Remaining attempts [{retry_attempts}] ..."
            )
            time.sleep(retry_timeout)
            return entry(retry_attempts=retry_attempts - 1, retry_timeout=retry_timeout)
    else:
        print(" [x] Exiting since all retrying attempts has been exhausted ...")


if __name__ == "__main__":
    try:
        entry()
    except KeyboardInterrupt:
        print(" [x] Interrupted ...")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
