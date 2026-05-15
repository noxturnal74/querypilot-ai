from app.core.config import get_settings
from app.services.ai.base import AIAdapter
from app.services.ai.mock import MockAIAdapter


def get_ai_adapter() -> AIAdapter:
    settings = get_settings()
    if settings.ai_provider == "mock":
        return MockAIAdapter()
    return MockAIAdapter()
