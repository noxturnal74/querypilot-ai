from app.services.ai.base import AIAdapter, AIAnalysisContext


class MockAIAdapter(AIAdapter):
    async def summarize(self, context: AIAnalysisContext) -> str:
        schema_note = " Schema context was included." if context.schema_text else ""
        return (
            "Mock AI review: prioritize the deterministic findings, validate recommendations "
            f"with EXPLAIN ANALYZE in {context.dialect}, and benchmark before rollout.{schema_note}"
        )
