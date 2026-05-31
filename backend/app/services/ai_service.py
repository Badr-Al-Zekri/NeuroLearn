from typing import Protocol
from fastapi import HTTPException
from pydantic import ValidationError
from app.core.config import get_settings
from app.models.schemas import ChatMessage, ChatResponse, QuizResponse, SummaryResponse
from app.services.gemini_client import GeminiClient
from app.services.mock_ai_client import MockAIClient


class AIClient(Protocol):
    async def summarize(self, *, title: str, content: str, tone: str) -> SummaryResponse: ...
    async def generate_quiz(self, *, title: str, content: str, question_count: int, difficulty: str) -> QuizResponse: ...
    async def chat(self, *, title: str, content: str, history: list[ChatMessage], message: str) -> ChatResponse: ...


def get_ai_client() -> AIClient:
    settings = get_settings()
    if settings.gemini_api_key:
        return GeminiClient(settings)
    return MockAIClient()


async def safe_ai_call(coro):
    try:
        return await coro
    except ValidationError as exc:
        raise HTTPException(status_code=502, detail="AI response did not match the expected schema.") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="AI generation failed. Please try again.") from exc

