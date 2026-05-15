from dataclasses import dataclass


@dataclass(frozen=True)
class AIAnalysisContext:
    query: str
    dialect: str
    schema_text: str | None
    deterministic_summary: str


class AIAdapter:
    async def summarize(self, context: AIAnalysisContext) -> str:
        raise NotImplementedError
