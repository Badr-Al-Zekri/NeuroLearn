from datetime import datetime, timezone
from uuid import uuid4
from app.models.schemas import (
    DocumentKind,
    DocumentRecord,
    DocumentResponse,
    KnowledgeRelationship,
    LearningConcept,
    LearningObjective,
    LearningTopic,
)


class DocumentStore:
    def __init__(self) -> None:
        self._documents: dict[str, DocumentRecord] = {}

    def create(self, *, title: str, kind: DocumentKind, content: str) -> DocumentRecord:
        cleaned = " ".join(content.split())
        record = DocumentRecord(
            document_id=str(uuid4()),
            title=title.strip() or "Untitled learning material",
            kind=kind,
            content=cleaned,
            word_count=len(cleaned.split()),
            created_at=datetime.now(timezone.utc),
        )
        self._documents[record.document_id] = record
        return record

    def get(self, document_id: str) -> DocumentRecord | None:
        return self._documents.get(document_id)

    def update_learning_model(
        self,
        *,
        document_id: str,
        normalized_content: str,
        chunk_count: int,
        concepts: list[LearningConcept],
        topics: list[LearningTopic],
        learning_objectives: list[LearningObjective],
        relationships: list[KnowledgeRelationship],
    ) -> DocumentRecord:
        record = self._documents[document_id]
        updated = record.model_copy(
            update={
                "content": normalized_content,
                "word_count": len(normalized_content.split()),
                "chunk_count": chunk_count,
                "concepts": concepts,
                "topics": topics,
                "learning_objectives": learning_objectives,
                "relationships": relationships,
            }
        )
        self._documents[document_id] = updated
        return updated

    def to_response(self, record: DocumentRecord) -> DocumentResponse:
        return DocumentResponse(
            document_id=record.document_id,
            title=record.title,
            kind=record.kind,
            word_count=record.word_count,
            chunk_count=record.chunk_count,
            created_at=record.created_at,
            features={"summary": True, "quiz": True, "chat": True, "insights": True, "rag": record.chunk_count > 0},
        )


document_store = DocumentStore()
