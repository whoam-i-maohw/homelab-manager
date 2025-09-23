import base64
import json
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.messages import DocumentMediaType, UserContent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
from src.domain.entity.error.ai import AIAgentRunningError
from src.domain.entity.ai.youtube import YouTubeVideoInsightsAnalysis
from src.ports.outbound.ai.generic_agent import GenericAIAgentInterface
import nest_asyncio

nest_asyncio.apply()


class YouTubeVideoInsightsAnalyzerAIAgent(
    GenericAIAgentInterface[YouTubeVideoInsightsAnalysis]
):
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

    def __encode_text_file_as_data_uri(self, *, txt: str) -> str:
        b64 = txt.encode().decode("utf-8")
        mime_type = "text/plain"
        return f"data:{mime_type};base64,{b64}"

    def run_agent(
        self,
        *,
        initial_prompt: str,
        video_subtitle_txt: str,
        response_in_json: bool = True,
        **kwargs,
    ) -> AIAgentRunningError | str | YouTubeVideoInsightsAnalysis:
        try:
            ollama_model = OpenAIChatModel(
                model_name=self.__ollama_model,
                provider=OllamaProvider(base_url=self.__ollama_base_url),
            )

            agent = Agent(
                ollama_model,
                system_prompt=(self.__agent_system_prompt),
            )

            if response_in_json:
                result = agent.run_sync(
                    [
                        f"{initial_prompt}, This is a file containing a YouTube video transcription,"
                        "- Summarize it in meaningful sentences."
                        "- Extract the main wisdom/insights."
                        "- Generate a list of the most relevant 10-20 topic tags."
                        "Respond in JSON:"
                        "{{'summary': '...', 'insights': ['...', '...'], 'tags': ['...', '...']}}",
                        BinaryContent(
                            data=video_subtitle_txt.encode(),
                            media_type="text/plain",
                        ),
                    ]
                )
                return YouTubeVideoInsightsAnalysis(
                    **json.loads(
                        result.output.replace("```json", "").replace("```", "").strip()
                    )
                )
            else:
                result = agent.run_sync(
                    f"{initial_prompt}, This is a transcription of a YouTube video,"
                    f"{video_subtitle_txt}"
                    "- Summarize it in meaningful sentences."
                    "- Extract the main wisdom/insights."
                    "- Generate a list of the most relevant 10-20 topic tags."
                )
                return result.output
        except Exception as ex:
            return AIAgentRunningError(
                error=str(ex),
                initial_prompt=initial_prompt,
                ollama_base_url=self.__ollama_base_url,
                ollama_model=self.__ollama_model,
            )
