from app.core.config import get_settings
from app.models.schemas import RetrievalRequest, RetrievalResponse, RetrievedChunk
from app.services.embedding_service import embedding_service
from app.services.vector_store import get_vector_store


class RetrieverService:
    async def retrieve(self, *, document_id: str | None, request: RetrievalRequest) -> RetrievalResponse:
        settings = get_settings()
        query_vector = await embedding_service.embed_query(request.query)
        chunks = await get_vector_store().search(
            query_vector=query_vector,
            top_k=request.top_k,
            document_id=document_id,
            topics=request.topics,
            difficulty=request.difficulty,
        )
        ranked = self._rank(request.query, chunks)
        grounded = [chunk for chunk in ranked if chunk.score >= settings.retrieval_min_score]
        return RetrievalResponse(query=request.query, chunks=grounded or ranked[: min(3, len(ranked))])

    def _rank(self, query: str, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        query_terms = {term.lower() for term in query.split() if len(term) > 3}
        reranked: list[RetrievedChunk] = []
        for chunk in chunks:
            chunk_terms = {term.lower().strip(".,;:!?()[]") for term in chunk.text.split()}
            lexical_bonus = min(0.08, 0.01 * len(query_terms.intersection(chunk_terms)))
            reranked.append(chunk.model_copy(update={"score": chunk.score + lexical_bonus}))
        return sorted(reranked, key=lambda item: item.score, reverse=True)


retriever_service = RetrieverService()

