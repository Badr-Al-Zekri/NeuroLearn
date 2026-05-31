import math
from datetime import timedelta
from app.models.learner import ConceptMastery, RetentionSnapshot
from app.services.learner_store import learner_store, utc_now


class RetentionService:
    def snapshots_for_learner(self, learner_id: str) -> list[RetentionSnapshot]:
        return [self.snapshot(mastery) for mastery in learner_store.list_mastery(learner_id)]

    def snapshot(self, mastery: ConceptMastery) -> RetentionSnapshot:
        now = utc_now()
        if mastery.last_studied_at is None:
            days_since = 999.0
        else:
            days_since = max(0.0, (now - mastery.last_studied_at).total_seconds() / 86400)
        half_life = self._half_life_days(mastery)
        decay_factor = math.exp(-days_since / half_life)
        retained = min(1.0, max(0.0, mastery.mastery_score * decay_factor))
        revision_due = retained < 0.62 or (mastery.next_review_at is not None and mastery.next_review_at <= now)
        next_review = mastery.next_review_at or now + timedelta(days=max(1, round(half_life / 2)))
        return RetentionSnapshot(
            learner_id=mastery.learner_id,
            concept_id=mastery.concept_id,
            retained_score=retained,
            decay_factor=max(0.0, min(1.0, decay_factor)),
            days_since_review=days_since,
            revision_due=revision_due,
            next_review_at=next_review,
            generated_at=now,
        )

    def _half_life_days(self, mastery: ConceptMastery) -> float:
        base = 2.0 + mastery.mastery_score * 12.0
        penalty = min(5.0, mastery.confusion_count * 1.5)
        bonus = min(4.0, mastery.revision_count * 0.8)
        return max(0.75, base - penalty + bonus)


retention_service = RetentionService()

