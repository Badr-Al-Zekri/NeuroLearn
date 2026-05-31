from datetime import timedelta
from app.models.learner import MasteryObservation, MasteryStatus, QuizResultEvent, StudyEventType
from app.services.learner_store import learner_store, utc_now


class MasteryService:
    def record_quiz_result(self, learner_id: str, event: QuizResultEvent):
        mastery = learner_store.get_mastery(learner_id, event.concept_id, event.concept_name)
        now = utc_now()
        delta = self._quiz_delta(event.correct, event.confidence, event.confusion_signal)
        score = min(1.0, max(0.0, mastery.mastery_score + delta))
        quiz_attempts = mastery.quiz_attempts + 1
        quiz_correct = mastery.quiz_correct + (1 if event.correct else 0)
        confusion_count = mastery.confusion_count + (1 if event.confusion_signal or not event.correct else 0)
        revision_count = mastery.revision_count + (0 if event.correct else 1)
        status = self._status(score, confusion_count, quiz_attempts, quiz_correct)
        next_review = self._next_review(now, score, confusion_count)
        observation = MasteryObservation(
            observed_at=now,
            source=StudyEventType.quiz_attempt,
            delta=delta,
            score_after=score,
            evidence=event.evidence,
        )
        updated = mastery.model_copy(
            update={
                "mastery_score": score,
                "confidence_score": min(1.0, max(0.0, (mastery.confidence_score + event.confidence) / 2 if mastery.quiz_attempts else event.confidence)),
                "quiz_attempts": quiz_attempts,
                "quiz_correct": quiz_correct,
                "confusion_count": confusion_count,
                "revision_count": revision_count,
                "last_studied_at": now,
                "next_review_at": next_review,
                "status": status,
                "observations": [*mastery.observations[-19:], observation],
            }
        )
        return learner_store.save_mastery(updated)

    def record_study_touch(self, learner_id: str, concept_id: str, concept_name: str, source: StudyEventType, evidence: str = ""):
        mastery = learner_store.get_mastery(learner_id, concept_id, concept_name)
        now = utc_now()
        delta = 0.03 if source in {StudyEventType.document_view, StudyEventType.retrieval, StudyEventType.chat} else 0.05
        score = min(1.0, mastery.mastery_score + delta)
        observation = MasteryObservation(observed_at=now, source=source, delta=delta, score_after=score, evidence=evidence)
        updated = mastery.model_copy(
            update={
                "mastery_score": score,
                "last_studied_at": now,
                "next_review_at": self._next_review(now, score, mastery.confusion_count),
                "status": self._status(score, mastery.confusion_count, mastery.quiz_attempts, mastery.quiz_correct),
                "observations": [*mastery.observations[-19:], observation],
            }
        )
        return learner_store.save_mastery(updated)

    def _quiz_delta(self, correct: bool, confidence: float, confused: bool) -> float:
        if correct and not confused:
            return 0.12 + 0.08 * confidence
        if correct and confused:
            return 0.04
        return -0.10 - 0.08 * confidence

    def _status(self, score: float, confusion_count: int, attempts: int, correct: int) -> MasteryStatus:
        accuracy = correct / attempts if attempts else 0
        if attempts == 0 and score == 0:
            return MasteryStatus.unseen
        if confusion_count >= 3 or (attempts >= 2 and accuracy < 0.5):
            return MasteryStatus.needs_revision
        if score >= 0.88:
            return MasteryStatus.mastered
        if score >= 0.68:
            return MasteryStatus.proficient
        if score >= 0.35:
            return MasteryStatus.developing
        return MasteryStatus.learning

    def _next_review(self, now, score: float, confusion_count: int):
        if score >= 0.85 and confusion_count == 0:
            return now + timedelta(days=14)
        if score >= 0.65:
            return now + timedelta(days=7)
        if score >= 0.35:
            return now + timedelta(days=2)
        return now + timedelta(hours=12)


mastery_service = MasteryService()

