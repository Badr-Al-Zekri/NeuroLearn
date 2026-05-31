import json
import re
import httpx
from app.core.config import Settings
from app.models.schemas import ChatMessage, ChatResponse, QuizResponse, SummaryResponse
from app.services.prompt_templates import PromptTemplates


class GeminiClient:
    def __init__(self, settings: Settings) -> None:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required for GeminiClient")
        self._api_key = settings.gemini_api_key
        self._model = settings.gemini_model
        self._base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent"

    async def _generate_json(self, prompt: str) -> dict:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                self._base_url,
                headers={"x-goog-api-key": self._api_key, "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
        text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return self._parse_json(text)

    def _parse_json(self, text: str) -> dict:
        cleaned = text.strip()
        fenced = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.DOTALL)
        if fenced:
            cleaned = fenced.group(1).strip()
        return json.loads(cleaned)

    async def summarize(self, *, title: str, content: str, tone: str) -> SummaryResponse:
        data = await self._generate_json(PromptTemplates.summary(title, content, tone))
        return SummaryResponse.model_validate(data)

    async def generate_quiz(self, *, title: str, content: str, question_count: int, difficulty: str) -> QuizResponse:
        data = await self._generate_json(PromptTemplates.quiz(title, content, question_count, difficulty))
        return QuizResponse.model_validate(data)

    async def chat(self, *, title: str, content: str, history: list[ChatMessage], message: str) -> ChatResponse:
        data = await self._generate_json(PromptTemplates.chat(title, content, history, message))
        return ChatResponse.model_validate(data)

