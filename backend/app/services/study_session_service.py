from app.models.learner import StudyEventRequest, StudyEventType
from app.services.learner_store import learner_store, utc_now
from app.services.learning_memory_service import learning_memory_service
from app.services.mastery_service import mastery_service


class StudySessionService:
    def start_session(self, learner_id: str, document_ids: list[str]):
        return learner_store.create_session(learner_id, document_ids)

    def record_event(self, learner_id: str, session_id: str, event: StudyEventRequest):
        session = learner_store.get_session(learner_id, session_id)
        if session is None:
            raise ValueError("Study session not found.")
        counts = dict(session.event_counts)
        counts[event.event_type.value] = counts.get(event.event_type.value, 0) + 1
        quiz_attempts = session.quiz_attempts
        quiz_accuracy = session.quiz_accuracy
        retrievals = session.retrieval_interactions + (1 if event.event_type == StudyEventType.retrieval else 0)
        chat_turns = session.chat_turns + (1 if event.event_type == StudyEventType.chat else 0)
        trends = dict(session.topic_difficulty_trends)

        if event.event_type == StudyEventType.quiz_attempt and event.concept_id and event.concept_name and event.correct is not None:
            mastery = mastery_service.record_quiz_result(
                learner_id,
                event=event_to_quiz_result(event),
            )
            learning_memory_service.remember_mastery_update(mastery)
            quiz_attempts += 1
            previous_correct = quiz_accuracy * (quiz_attempts - 1)
            quiz_accuracy = (previous_correct + (1 if event.correct else 0)) / quiz_attempts
            trends[event.concept_name] = 1 - mastery.mastery_score
        elif event.concept_id and event.concept_name:
            mastery = mastery_service.record_study_touch(learner_id, event.concept_id, event.concept_name, event.event_type)
            learning_memory_service.remember_mastery_update(mastery)

        learning_memory_service.remember_event(learner_id, event.event_type, event.concept_id)
        now = utc_now()
        duration = int((now - session.started_at).total_seconds())
        engagement = self._engagement_score(counts, duration)
        updated = session.model_copy(
            update={
                "duration_seconds": duration,
                "event_counts": counts,
                "quiz_attempts": quiz_attempts,
                "quiz_accuracy": quiz_accuracy,
                "retrieval_interactions": retrievals,
                "chat_turns": chat_turns,
                "topic_difficulty_trends": trends,
                "engagement_score": engagement,
            }
        )
        return learner_store.save_session(updated)

    def end_session(self, learner_id: str, session_id: str):
        session = learner_store.get_session(learner_id, session_id)
        if session is None:
            raise ValueError("Study session not found.")
        now = utc_now()
        updated = session.model_copy(update={"ended_at": now, "duration_seconds": int((now - session.started_at).total_seconds())})
        return learner_store.save_session(updated)

    def _engagement_score(self, counts: dict[str, int], duration_seconds: int) -> float:
        weighted = (
            counts.get(StudyEventType.retrieval.value, 0) * 0.16
            + counts.get(StudyEventType.chat.value, 0) * 0.12
            + counts.get(StudyEventType.quiz_attempt.value, 0) * 0.22
            + counts.get(StudyEventType.revision.value, 0) * 0.18
            + min(duration_seconds / 1800, 1) * 0.20
        )
        return min(1.0, weighted)


def event_to_quiz_result(event: StudyEventRequest):
    from app.models.learner import QuizResultEvent

    return QuizResultEvent(
        concept_id=event.concept_id or "unknown",
        concept_name=event.concept_name or "Unknown concept",
        correct=bool(event.correct),
        confidence=event.confidence,
        confusion_signal=bool(event.metadata.get("confusion_signal", False)),
        evidence=str(event.metadata.get("evidence", "")),
    )


study_session_service = StudySessionService()

