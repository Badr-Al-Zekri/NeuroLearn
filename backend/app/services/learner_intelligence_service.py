from app.models.learner import LearnerIntelligenceSnapshot, QuizResultEvent
from app.services.learner_store import learner_store
from app.services.learning_memory_service import learning_memory_service
from app.services.mastery_service import mastery_service
from app.services.recommendation_service import recommendation_service
from app.services.retention_service import retention_service


class LearnerIntelligenceService:
    def profile(self, learner_id: str):
        return learner_store.get_or_create_profile(learner_id)

    def record_quiz_result(self, learner_id: str, event: QuizResultEvent):
        mastery = mastery_service.record_quiz_result(learner_id, event)
        learning_memory_service.remember_mastery_update(mastery)
        return mastery

    def snapshot(self, learner_id: str) -> LearnerIntelligenceSnapshot:
        profile = learner_store.get_or_create_profile(learner_id)
        mastery = learner_store.list_mastery(learner_id)
        return LearnerIntelligenceSnapshot(
            profile=profile,
            memory=learner_store.get_memory(learner_id),
            mastery=mastery,
            weakness_profile=recommendation_service.weakness_profile(learner_id),
            recommendations=recommendation_service.recommendations(learner_id),
            retention=retention_service.snapshots_for_learner(learner_id),
            active_sessions=[session for session in learner_store.list_sessions(learner_id) if session.ended_at is None],
        )


learner_intelligence_service = LearnerIntelligenceService()

