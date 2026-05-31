from app.models.schemas import DocumentKind, DocumentRecord, ProcessedDocument
from app.services.document_processor import document_processor
from app.services.document_store import document_store
from app.services.embedding_service import embedding_service
from app.services.knowledge_model import knowledge_model_service
from app.services.vector_store import get_vector_store


class LearningOrchestrator:
    async def ingest_document(self, *, title: str, kind: DocumentKind, content: str) -> DocumentRecord:
        raw_record = document_store.create(title=title, kind=kind, content=content)
        processed = document_processor.process(
            document_id=raw_record.document_id,
            title=raw_record.title,
            kind=raw_record.kind,
            raw_text=content,
        )
        await self.index_processed_document(processed)
        return document_store.update_learning_model(
            document_id=raw_record.document_id,
            normalized_content=processed.normalized_text,
            chunk_count=len(processed.chunks),
            concepts=processed.concepts,
            topics=processed.topics,
            learning_objectives=processed.learning_objectives,
            relationships=processed.relationships,
        )

    async def index_processed_document(self, processed: ProcessedDocument) -> None:
        embeddings = await embedding_service.embed_chunks(processed.chunks)
        await get_vector_store().upsert_chunks(processed.chunks, embeddings)
        knowledge_model_service.build_study_metadata(processed)
        knowledge_model_service.analytics_snapshot(processed)


learning_orchestrator = LearningOrchestrator()
