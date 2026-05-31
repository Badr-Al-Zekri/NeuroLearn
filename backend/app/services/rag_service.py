from app.core.config import get_settings
from app.models.schemas import ChatMessage, ChatResponse, RetrievalRequest, RetrievalResponse
from app.services.ai_orchestrator import ai_orchestrator
from app.services.context_builder import context_builder
from app.services.document_store import document_store
from app.services.retriever import retriever_service


class RagService:
    async def retrieve(
        self,
        *,
        document_id: str,
        query: str,
        top_k: int | None = None,
        topics: list[str] | None = None,
        difficulty: str = "any",
    ) -> RetrievalResponse:
        settings = get_settings()
        request = RetrievalRequest(query=query, top_k=top_k or settings.retrieval_top_k, topics=topics or [], difficulty=difficulty)
        return await retriever_service.retrieve(document_id=document_id, request=request)

    async def grounded_chat(self, *, document_id: str, history: list[ChatMessage], message: str) -> ChatResponse:
        document = document_store.get(document_id)
        if document is None:
            raise ValueError("Document not found.")
        retrieval = await self.retrieve(document_id=document_id, query=message)
        context = context_builder.build(retrieval.chunks)
        if not context:
            context = document.content[:8000]
        return await ai_orchestrator.generate_grounded_chat(
            title=document.title,
            context=context,
            history=history,
            message=message,
            source_chunks=retrieval.chunks,
        )


rag_service = RagService()
