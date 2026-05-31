from app.models.learner import ConceptMastery, StudyEventType
from app.services.learner_store import learner_store


class LearningMemoryService:
    def remember_mastery_update(self, mastery: ConceptMastery) -> None:
        memory = learner_store.get_memory(mastery.learner_id)
        studied = self._append_unique(memory.studied_concept_ids, mastery.concept_id)
        failed = memory.failed_concept_ids
        mistakes = dict(memory.repeated_mistakes)
        revisions = memory.revision_history
        history = self._append_limited(memory.learning_history, f"{mastery.concept_name}:{mastery.status.value}:{mastery.mastery_score:.2f}")
        if mastery.status.value == "needs_revision":
            failed = self._append_unique(failed, mastery.concept_id)
            mistakes[mastery.concept_id] = mistakes.get(mastery.concept_id, 0) + 1
            revisions = self._append_limited(revisions, mastery.concept_id)
        learner_store.save_memory(
            memory.model_copy(
                update={
                    "studied_concept_ids": studied,
                    "failed_concept_ids": failed,
                    "repeated_mistakes": mistakes,
                    "learning_history": history,
                    "revision_history": revisions,
                }
            )
        )

    def remember_event(self, learner_id: str, event_type: StudyEventType, concept_id: str | None = None) -> None:
        memory = learner_store.get_memory(learner_id)
        history = self._append_limited(memory.learning_history, f"{event_type.value}:{concept_id or 'general'}")
        learner_store.save_memory(memory.model_copy(update={"learning_history": history}))

    def _append_unique(self, values: list[str], value: str) -> list[str]:
        return values if value in values else [*values, value]

    def _append_limited(self, values: list[str], value: str, limit: int = 80) -> list[str]:
        return [*values, value][-limit:]


learning_memory_service = LearningMemoryService()

