import json
import os
from pathlib import Path
import base64
from tempfile import gettempdir
from urllib.parse import urlparse
import urllib.request
from pydantic_ai import Agent, ImageUrl
from src.domain.entity.error.ai import AIAgentRunningError
from src.domain.entity.ai.nutrition_breakdown import NutritionBreakdown
from src.ports.outbound.ai.generic_agent import GenericAIAgentInterface
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
import nest_asyncio

nest_asyncio.apply()


class NutritionBreakdownAIAgent(GenericAIAgentInterface[NutritionBreakdown]):
    def __init__(
        self,
        *,
        ollama_base_url: str,
        ollama_model: str,
        agent_system_prompt: str,
    ) -> None:
        self.__ollama_base_url = ollama_base_url
        self.__ollama_model = ollama_model
        self.__agent_system_prompt = agent_system_prompt

    def __download_image(
        self,
        *,
        image_url: str,
        base_dir: str = gettempdir(),
    ) -> str:
        parsed_url = urlparse(image_url)
        image_name = os.path.basename(parsed_url.path)
        image_file_path: str = os.path.join(base_dir, image_name)

        print(" [x] Downloading the image ...")
        urllib.request.urlretrieve(image_url, image_file_path)
        print(f" [x] Image saved as {image_name} ...")
        return image_file_path

    def __encode_image_as_data_uri(self, *, path: str) -> str:
        data = Path(path).read_bytes()
        b64 = base64.b64encode(data).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"

    def run_agent(
        self, *, initial_prompt: str, image_uri: str, **kwargs
    ) -> AIAgentRunningError | NutritionBreakdown:
        try:
            ollama_model = OpenAIChatModel(
                model_name=self.__ollama_model,
                provider=OllamaProvider(base_url=self.__ollama_base_url),
            )

            agent = Agent(
                ollama_model,
                system_prompt=(self.__agent_system_prompt),
            )

            image_url: ImageUrl
            if image_uri.startswith("http"):
                image_file_path: str = self.__download_image(image_url=image_uri)
                data_uri = self.__encode_image_as_data_uri(path=image_file_path)
                image_url = ImageUrl(data_uri)
            else:
                data_uri = self.__encode_image_as_data_uri(path=image_uri)
                image_url = ImageUrl(data_uri)

            print(" [x] Processing getting nutrition flow ...")

            result = agent.run_sync(
                [
                    f"{initial_prompt}, The plate is in average 27 cm, "
                    "give me the nutrition breakdown for what's in the image, ",
                    "Response only in JSON format of the nutrition breakdown "
                    "of what's in the image with those keys inside the JSON Response, "
                    "summary (what's actually inside the meal), calories, protein, "
                    "carbohydrates, fiber, fats, saturated fat, sugar and sodium, "
                    "note that, "
                    "calories in kcal, "
                    "protein in grams, "
                    "carbohydrates in grams, "
                    "fiber in grams, "
                    "fats in grams, "
                    "saturated_fat in grams, "
                    "sugar in grams, "
                    "sodium in grams."
                    "So write the units in the values of the JSON response always.",
                    image_url,
                ]
            )

            return NutritionBreakdown(
                **json.loads(
                    result.output.replace("```json", "").replace("```", "").strip()
                )
            )
        except Exception as ex:
            return AIAgentRunningError(
                error=str(ex),
                initial_prompt=initial_prompt,
                ollama_base_url=self.__ollama_base_url,
                ollama_model=self.__ollama_model,
            )
