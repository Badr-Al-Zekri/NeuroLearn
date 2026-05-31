import hashlib
import math
import httpx
from app.core.config import Settings, get_settings
from app.models.schemas import DocumentChunk, EmbeddingVector


class EmbeddingService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    async def embed_chunks(self, chunks: list[DocumentChunk]) -> list[EmbeddingVector]:
        texts = [(chunk.chunk_id, chunk.text) for chunk in chunks]
        return await self.embed_texts(texts)

    async def embed_query(self, query: str) -> list[float]:
        vector = (await self.embed_texts([("query", query)]))[0]
        return vector.values

    async def embed_texts(self, texts: list[tuple[str, str]]) -> list[EmbeddingVector]:
        if not texts:
            return []
        if self._settings.embedding_provider == "gemini" and self._settings.gemini_api_key:
            return await self._gemini_embeddings(texts)
        return [
            EmbeddingVector(
                text_id=text_id,
                values=self._mock_embedding(text),
                provider="mock",
                model="mock-hash",
                dimensions=self._settings.embedding_dimensions,
                metadata={"source": "deterministic-local"},
            )
            for text_id, text in texts
        ]

    async def _gemini_embeddings(self, texts: list[tuple[str, str]]) -> list[EmbeddingVector]:
        results: list[EmbeddingVector] = []
        batch_size = max(1, self._settings.embedding_batch_size)
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            payload = {
                "requests": [
                    {
                        "model": f"models/{self._settings.embedding_model}",
                        "content": {"parts": [{"text": text}]},
                        "outputDimensionality": self._settings.embedding_dimensions,
                    }
                    for _, text in batch
                ]
            }
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._settings.embedding_model}:batchEmbedContents"
            async with httpx.AsyncClient(timeout=45) as client:
                response = await client.post(
                    url,
                    headers={"x-goog-api-key": self._settings.gemini_api_key, "Content-Type": "application/json"},
                    json=payload,
                )
                response.raise_for_status()
            embeddings = response.json()["embeddings"]
            for (text_id, _), embedding in zip(batch, embeddings, strict=True):
                results.append(
                    EmbeddingVector(
                        text_id=text_id,
                        values=embedding["values"],
                        provider="gemini",
                        model=self._settings.embedding_model,
                        dimensions=len(embedding["values"]),
                        metadata={"batch_size": len(batch)},
                    )
                )
        return results

    def _mock_embedding(self, text: str) -> list[float]:
        dimensions = self._settings.embedding_dimensions
        vector = [0.0] * dimensions
        tokens = [token.lower() for token in text.split() if token.strip()]
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        magnitude = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / magnitude for value in vector]


embedding_service = EmbeddingService()
