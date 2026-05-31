from app.models.schemas import LearningAnalyticsSnapshot, ProcessedDocument, StudyMetadata, TutorMemory


class KnowledgeModelService:
    def build_study_metadata(self, processed: ProcessedDocument) -> StudyMetadata:
        words = len(processed.normalized_text.split())
        difficulty_rank = {"introductory": 0, "intermediate": 1, "advanced": 2}
        chunk_difficulties = [chunk.metadata.difficulty for chunk in processed.chunks]
        difficulty = max(chunk_difficulties or ["introductory"], key=lambda item: difficulty_rank[getattr(item, "value", item)])
        primary_topics = [topic.name for topic in processed.topics] or [item for chunk in processed.chunks for item in chunk.metadata.topics[:2]][:4]
        return StudyMetadata(
            document_id=processed.document_id,
            estimated_reading_minutes=max(1, round(words / 220)),
            difficulty=difficulty,
            primary_topics=primary_topics,
            concept_count=len(processed.concepts),
            chunk_count=len(processed.chunks),
        )

    def starter_memory(self) -> TutorMemory:
        return TutorMemory()

    def analytics_snapshot(self, processed: ProcessedDocument) -> LearningAnalyticsSnapshot:
        weak_topics = [concept.name for concept in processed.concepts if getattr(concept.difficulty, "value", concept.difficulty) == "advanced"][:5]
        return LearningAnalyticsSnapshot(document_id=processed.document_id, weak_topics=weak_topics)


knowledge_model_service = KnowledgeModelService()
