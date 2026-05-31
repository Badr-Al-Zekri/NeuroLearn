from hashlib import sha256
from app.models.learner import (
    ConceptMastery,
    RecommendationItem,
    RecommendationProfile,
    RecommendationType,
    WeaknessProfile,
)
from app.services.learner_store import learner_store, utc_now
from app.services.retention_service import retention_service


class RecommendationService:
    def weakness_profile(self, learner_id: str) -> WeaknessProfile:
        mastery = learner_store.list_mastery(learner_id)
        weak = [item for item in mastery if item.mastery_score < 0.55 or item.status.value == "needs_revision"]
        low_accuracy = [
            item.concept_id
            for item in mastery
            if item.quiz_attempts >= 2 and (item.quiz_correct / item.quiz_attempts) < 0.6
        ]
        confusion = {item.concept_id: item.confusion_count for item in mastery if item.confusion_count > 0}
        due = [snapshot.concept_id for snapshot in retention_service.snapshots_for_learner(learner_id) if snapshot.revision_due]
        return WeaknessProfile(
            learner_id=learner_id,
            weak_concept_ids=[item.concept_id for item in weak],
            confusion_indicators=confusion,
            low_accuracy_concepts=low_accuracy,
            revision_needed_concepts=due,
            generated_at=utc_now(),
        )

    def recommendations(self, learner_id: str) -> RecommendationProfile:
        mastery = learner_store.list_mastery(learner_id)
        weakness = self.weakness_profile(learner_id)
        items: list[RecommendationItem] = []
        for item in sorted(mastery, key=lambda value: value.mastery_score)[:5]:
            if item.concept_id in weakness.revision_needed_concepts:
                items.append(self._item(item, RecommendationType.retention_review, 0.92, "Retention score is decaying and review is due."))
            elif item.concept_id in weakness.weak_concept_ids:
                items.append(self._item(item, RecommendationType.revise_weak_concept, 0.84, "Mastery score is below the current proficiency threshold."))
            elif item.quiz_attempts == 0:
                items.append(self._item(item, RecommendationType.practice_quiz, 0.66, "No quiz evidence exists for this concept yet."))

        if not items and mastery:
            next_item = sorted(mastery, key=lambda value: value.last_studied_at or utc_now())[0]
            items.append(self._item(next_item, RecommendationType.next_topic, 0.55, "Continue progression by revisiting the least recently studied concept."))

        return RecommendationProfile(learner_id=learner_id, recommendations=items[:6], generated_at=utc_now())

    def _item(self, mastery: ConceptMastery, recommendation_type: RecommendationType, priority: float, rationale: str) -> RecommendationItem:
        recommendation_id = sha256(f"{mastery.learner_id}:{mastery.concept_id}:{recommendation_type.value}".encode("utf-8")).hexdigest()[:12]
        title = {
            RecommendationType.retention_review: f"Review {mastery.concept_name}",
            RecommendationType.revise_weak_concept: f"Strengthen {mastery.concept_name}",
            RecommendationType.practice_quiz: f"Take a short quiz on {mastery.concept_name}",
            RecommendationType.next_topic: f"Continue with {mastery.concept_name}",
            RecommendationType.tutoring_prompt: f"Ask the tutor about {mastery.concept_name}",
        }[recommendation_type]
        return RecommendationItem(
            recommendation_id=recommendation_id,
            recommendation_type=recommendation_type,
            title=title,
            rationale=rationale,
            concept_id=mastery.concept_id,
            priority=priority,
            metadata={"mastery_score": round(mastery.mastery_score, 3), "status": mastery.status.value},
        )


recommendation_service = RecommendationService()

