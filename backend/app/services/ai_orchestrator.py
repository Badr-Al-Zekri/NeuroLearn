from app.models.schemas import ChatMessage, ChatResponse, RetrievedChunk
from app.services.ai_service import get_ai_client, safe_ai_call
from app.services.reasoning_layer import reasoning_layer
from app.services.response_validator import response_validator


class AIOrchestrator:
    async def generate_grounded_chat(
        self,
        *,
        title: str,
        context: str,
        history: list[ChatMessage],
        message: str,
        source_chunks: list[RetrievedChunk],
    ) -> ChatResponse:
        plan = reasoning_layer.plan_grounded_tutor_response(message=message, chunks=source_chunks)
        grounded_message = f"{message}\n\nReasoning plan for the tutor:\n{plan.to_prompt_directive()}"
        ai = get_ai_client()
        response = await safe_ai_call(ai.chat(title=title, content=context, history=history, message=grounded_message))
        response = response_validator.validate_model(response, ChatResponse)
        clean_answer = response_validator.ensure_grounded_answer(response.answer)
        cited = response.cited_insights or [chunk.metadata.heading or f"Chunk {chunk.metadata.chunk_index + 1}" for chunk in source_chunks[:4]]
        return response.model_copy(update={"answer": clean_answer, "cited_insights": cited, "source_chunks": source_chunks})


ai_orchestrator = AIOrchestrator()

