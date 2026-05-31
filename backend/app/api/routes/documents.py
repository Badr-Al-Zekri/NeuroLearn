from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from app.core.config import get_settings
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    DocumentKind,
    DocumentResponse,
    QuizRequest,
    QuizResponse,
    RetrievalRequest,
    RetrievalResponse,
    SummaryRequest,
    SummaryResponse,
    TextUploadRequest,
)
from app.services.ai_service import get_ai_client, safe_ai_call
from app.services.document_store import document_store
from app.services.learning_orchestrator import learning_orchestrator
from app.services.pdf_extractor import PdfExtractionError, extract_pdf_text
from app.services.rag_service import rag_service

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _require_document(document_id: str):
    document = document_store.get(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return document


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    title: str = Form(default="Untitled learning material"),
    text: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
) -> DocumentResponse:
    settings = get_settings()
    if file is None and not text:
        raise HTTPException(status_code=400, detail="Upload a PDF or provide text.")

    if file is not None:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")
        data = await file.read()
        if len(data) > settings.max_upload_mb * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"PDF uploads are limited to {settings.max_upload_mb} MB.")
        try:
            content = extract_pdf_text(data)
        except PdfExtractionError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        record = await learning_orchestrator.ingest_document(title=title or file.filename or "PDF upload", kind=DocumentKind.pdf, content=content)
        return document_store.to_response(record)

    if len((text or "").split()) < 20:
        raise HTTPException(status_code=400, detail="Text uploads need at least 20 words.")
    request = TextUploadRequest(title=title, text=text or "")
    record = await learning_orchestrator.ingest_document(title=request.title, kind=DocumentKind.text, content=request.text)
    return document_store.to_response(record)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str) -> DocumentResponse:
    return document_store.to_response(_require_document(document_id))


@router.get("/{document_id}/knowledge")
async def get_document_knowledge(document_id: str):
    document = _require_document(document_id)
    return {
        "document_id": document.document_id,
        "concepts": document.concepts,
        "topics": document.topics,
        "learning_objectives": document.learning_objectives,
        "relationships": document.relationships,
        "study_metadata": {
            "chunk_count": document.chunk_count,
            "concept_count": len(document.concepts),
            "topic_count": len(document.topics),
            "objective_count": len(document.learning_objectives),
            "relationship_count": len(document.relationships),
        },
    }


@router.post("/{document_id}/retrieve", response_model=RetrievalResponse)
async def retrieve_document_context(document_id: str, request: RetrievalRequest) -> RetrievalResponse:
    _require_document(document_id)
    return await rag_service.retrieve(
        document_id=document_id,
        query=request.query,
        top_k=request.top_k,
        topics=request.topics,
        difficulty=request.difficulty,
    )


@router.post("/{document_id}/summary", response_model=SummaryResponse)
async def summarize_document(document_id: str, request: SummaryRequest) -> SummaryResponse:
    document = _require_document(document_id)
    ai = get_ai_client()
    return await safe_ai_call(ai.summarize(title=document.title, content=document.content, tone=request.tone))


@router.post("/{document_id}/quiz", response_model=QuizResponse)
async def quiz_document(document_id: str, request: QuizRequest) -> QuizResponse:
    document = _require_document(document_id)
    ai = get_ai_client()
    return await safe_ai_call(
        ai.generate_quiz(
            title=document.title,
            content=document.content,
            question_count=request.question_count,
            difficulty=request.difficulty,
        )
    )


@router.post("/{document_id}/chat", response_model=ChatResponse)
async def chat_with_document(document_id: str, request: ChatRequest) -> ChatResponse:
    _require_document(document_id)
    try:
        return await rag_service.grounded_chat(document_id=document_id, history=request.history, message=request.message)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
