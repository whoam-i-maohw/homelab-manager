from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class YouTubeVideoInsightsAnalysis:
    summary: str
    insights: list[str]
    tags: list[str]
