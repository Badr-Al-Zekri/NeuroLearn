from collections import defaultdict
from uuid import UUID, uuid5
from app.core.config import Settings, get_settings
from app.models.schemas import DocumentChunk, EmbeddingVector, RetrievedChunk

QDRANT_NAMESPACE = UUID("f54f97b2-a7aa-4972-841b-0b908bc1a1d7")


class VectorStore:
    async def ensure_collection(self) -> None:
        raise NotImplementedError

    async def upsert_chunks(self, chunks: list[DocumentChunk], embeddings: list[EmbeddingVector]) -> None:
        raise NotImplementedError

    async def search(
        self,
        *,
        query_vector: list[float],
        top_k: int,
        document_id: str | None = None,
        topics: list[str] | None = None,
        difficulty: str = "any",
    ) -> list[RetrievedChunk]:
        raise NotImplementedError


class InMemoryVectorStore(VectorStore):
    def __init__(self) -> None:
        self._vectors: dict[str, list[float]] = {}
        self._chunks: dict[str, DocumentChunk] = {}
        self._document_index: dict[str, set[str]] = defaultdict(set)

    async def ensure_collection(self) -> None:
        return None

    async def upsert_chunks(self, chunks: list[DocumentChunk], embeddings: list[EmbeddingVector]) -> None:
        embedding_map = {embedding.text_id: embedding.values for embedding in embeddings}
        for chunk in chunks:
            vector = embedding_map.get(chunk.chunk_id)
            if vector is None:
                continue
            self._vectors[chunk.chunk_id] = vector
            self._chunks[chunk.chunk_id] = chunk
            self._document_index[chunk.metadata.document_id].add(chunk.chunk_id)

    async def search(
        self,
        *,
        query_vector: list[float],
        top_k: int,
        document_id: str | None = None,
        topics: list[str] | None = None,
        difficulty: str = "any",
    ) -> list[RetrievedChunk]:
        topics = topics or []
        candidate_ids = self._document_index.get(document_id, set()) if document_id else set(self._chunks)
        scored: list[RetrievedChunk] = []
        for chunk_id in candidate_ids:
            chunk = self._chunks[chunk_id]
            if difficulty != "any" and chunk.metadata.difficulty != difficulty:
                continue
            if topics and not set(topics).intersection(chunk.metadata.topics):
                continue
            score = self._cosine(query_vector, self._vectors[chunk_id])
            scored.append(RetrievedChunk(chunk_id=chunk.chunk_id, text=chunk.text, score=score, metadata=chunk.metadata))
        return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]

    def _cosine(self, left: list[float], right: list[float]) -> float:
        if not left or not right:
            return 0.0
        dot = sum(a * b for a, b in zip(left, right, strict=False))
        left_mag = sum(a * a for a in left) ** 0.5
        right_mag = sum(b * b for b in right) ** 0.5
        return dot / ((left_mag * right_mag) or 1.0)


class QdrantVectorStore(VectorStore):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        try:
            from qdrant_client import AsyncQdrantClient, models
        except ImportError as exc:
            raise RuntimeError("qdrant-client is required when VECTOR_STORE_PROVIDER=qdrant") from exc
        self._client = AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
        self._models = models

    async def ensure_collection(self) -> None:
        if await self._client.collection_exists(self._settings.qdrant_collection):
            return
        await self._client.create_collection(
            collection_name=self._settings.qdrant_collection,
            vectors_config=self._models.VectorParams(
                size=self._settings.embedding_dimensions,
                distance=self._models.Distance.COSINE,
            ),
        )

    async def upsert_chunks(self, chunks: list[DocumentChunk], embeddings: list[EmbeddingVector]) -> None:
        await self.ensure_collection()
        embedding_map = {embedding.text_id: embedding.values for embedding in embeddings}
        points = []
        for chunk in chunks:
            vector = embedding_map.get(chunk.chunk_id)
            if vector is None:
                continue
            payload = chunk.metadata.model_dump(mode="json") | {"chunk_id": chunk.chunk_id, "text": chunk.text}
            points.append(
                self._models.PointStruct(
                    id=str(uuid5(QDRANT_NAMESPACE, chunk.chunk_id)),
                    vector=vector,
                    payload=payload,
                )
            )
        if points:
            await self._client.upsert(collection_name=self._settings.qdrant_collection, points=points)

    async def search(
        self,
        *,
        query_vector: list[float],
        top_k: int,
        document_id: str | None = None,
        topics: list[str] | None = None,
        difficulty: str = "any",
    ) -> list[RetrievedChunk]:
        await self.ensure_collection()
        conditions = []
        if document_id:
            conditions.append(self._models.FieldCondition(key="document_id", match=self._models.MatchValue(value=document_id)))
        if topics:
            conditions.append(self._models.FieldCondition(key="topics", match=self._models.MatchAny(any=topics)))
        if difficulty != "any":
            conditions.append(self._models.FieldCondition(key="difficulty", match=self._models.MatchValue(value=difficulty)))
        query_filter = self._models.Filter(must=conditions) if conditions else None
        response = await self._client.query_points(
            collection_name=self._settings.qdrant_collection,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
        )
        return [self._hit_to_chunk(hit) for hit in response.points]

    def _hit_to_chunk(self, hit) -> RetrievedChunk:
        from app.models.schemas import ChunkMetadata

        payload = hit.payload or {}
        text = payload.pop("text", "")
        chunk_id = payload.pop("chunk_id", str(hit.id))
        return RetrievedChunk(
            chunk_id=chunk_id,
            text=text,
            score=float(hit.score),
            metadata=ChunkMetadata.model_validate(payload),
        )


memory_vector_store = InMemoryVectorStore()


def get_vector_store() -> VectorStore:
    settings = get_settings()
    if settings.vector_store_provider == "qdrant":
        return QdrantVectorStore(settings)
    return memory_vector_store
