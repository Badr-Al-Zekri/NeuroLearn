from app.models.adaptive import (
    AdaptiveDecision,
    CognitiveLoadLevel,
    CognitiveLoadSnapshot,
    LearningPathAction,
    LearningPathNode,
    PersonalizedLearningPath,
    QuizDifficultyDecision,
    QuizDifficultyLevel,
    RevisionDecision,
    TutoringMode,
    TutoringStrategy,
)
from app.models.learner import ConceptMastery, RecommendationItem, RecommendationType, RetentionSnapshot, StudySession
from app.services.learner_store import learner_store
from app.services.recommendation_service import recommendation_service
from app.services.retention_service import retention_service


class AdaptiveDecisionEngine:
    def decision(self, learner_id: str, concept_id: str | None = None) -> AdaptiveDecision:
        learner_store.get_or_create_profile(learner_id)
        mastery = learner_store.list_mastery(learner_id)
        active_sessions = [session for session in learner_store.list_sessions(learner_id) if session.ended_at is None]
        retention = retention_service.snapshots_for_learner(learner_id)
        cognitive_load = self.cognitive_load(learner_id, active_sessions)
        ranked = self.rank_recommendations(learner_id, retention, cognitive_load)
        selected = self._select_mastery(mastery, concept_id)
        tutoring = self.tutoring_strategy(learner_id, selected, cognitive_load)
        quiz = self.quiz_difficulty(learner_id, selected, retention) if selected else None
        path = self.learning_path(learner_id, mastery, retention)
        revision = self.revision_priorities(learner_id, mastery, retention)
        explainability = [
            "Recommendation ranking combines base priority, retention urgency, weakness indicators, and cognitive load.",
            "Tutoring mode is selected from mastery, confusion, quiz evidence, and fatigue signals.",
            "Quiz difficulty is deterministic and can later be replaced by a learned policy.",
            "Learning path advancement is gated by mastery and prerequisite weakness.",
        ]
        return AdaptiveDecision(
            learner_id=learner_id,
            ranked_recommendations=ranked,
            tutoring_strategy=tutoring,
            quiz_difficulty=quiz,
            learning_path=path,
            revision_priorities=revision,
            cognitive_load=cognitive_load,
            explainability=explainability,
        )

    def rank_recommendations(
        self,
        learner_id: str,
        retention: list[RetentionSnapshot] | None = None,
        cognitive_load: CognitiveLoadSnapshot | None = None,
    ) -> list[RecommendationItem]:
        retention = retention or retention_service.snapshots_for_learner(learner_id)
        cognitive_load = cognitive_load or self.cognitive_load(learner_id)
        due = {item.concept_id: item for item in retention if item.revision_due}
        weakness = recommendation_service.weakness_profile(learner_id)
        ranked: list[RecommendationItem] = []
        for item in recommendation_service.recommendations(learner_id).recommendations:
            priority = item.priority
            if item.concept_id in due:
                priority += 0.12 + (1 - due[item.concept_id].retained_score) * 0.18
            if item.concept_id in weakness.weak_concept_ids:
                priority += 0.08
            if cognitive_load.overload_detected and item.recommendation_type in {RecommendationType.practice_quiz, RecommendationType.next_topic}:
                priority -= 0.18
            metadata = dict(item.metadata) | {"adaptive_ranked": True, "cognitive_load": cognitive_load.load_level.value}
            ranked.append(item.model_copy(update={"priority": max(0.0, min(1.0, priority)), "metadata": metadata}))
        return sorted(ranked, key=lambda item: item.priority, reverse=True)

    def tutoring_strategy(
        self,
        learner_id: str,
        mastery: ConceptMastery | None,
        cognitive_load: CognitiveLoadSnapshot | None = None,
    ) -> TutoringStrategy:
        cognitive_load = cognitive_load or self.cognitive_load(learner_id)
        if mastery is None:
            mode = TutoringMode.beginner
            rationale = "No concept-specific mastery evidence exists yet."
        elif cognitive_load.overload_detected:
            mode = TutoringMode.step_by_step
            rationale = "Cognitive load is elevated, so the tutor should reduce pace and sequence guidance."
        elif mastery.confusion_count >= 2 or mastery.mastery_score < 0.35:
            mode = TutoringMode.beginner
            rationale = "Low mastery or repeated confusion indicates foundational scaffolding is needed."
        elif mastery.quiz_attempts >= 2 and mastery.quiz_correct / mastery.quiz_attempts < 0.6:
            mode = TutoringMode.step_by_step
            rationale = "Quiz evidence shows repeated mistakes, so guided repair is preferred."
        elif mastery.mastery_score >= 0.82:
            mode = TutoringMode.exam_preparation
            rationale = "High mastery supports exam-style transfer and challenge."
        elif mastery.confidence_score < 0.45:
            mode = TutoringMode.deep_explanation
            rationale = "Moderate mastery with low confidence benefits from richer explanation."
        else:
            mode = TutoringMode.concise
            rationale = "Current evidence supports focused, efficient tutoring."

        directives = self._mode_directives(mode)
        return TutoringStrategy(
            learner_id=learner_id,
            concept_id=mastery.concept_id if mastery else None,
            mode=mode,
            explanation_depth=self._explanation_depth(mode),
            interaction_style=self._interaction_style(mode),
            prompt_directives=directives,
            rationale=rationale,
        )

    def quiz_difficulty(
        self,
        learner_id: str,
        mastery: ConceptMastery,
        retention: list[RetentionSnapshot] | None = None,
    ) -> QuizDifficultyDecision:
        retention = retention or retention_service.snapshots_for_learner(learner_id)
        retained = next((item.retained_score for item in retention if item.concept_id == mastery.concept_id), mastery.mastery_score)
        mistake_pressure = min(1.0, mastery.confusion_count * 0.18 + max(0, mastery.quiz_attempts - mastery.quiz_correct) * 0.12)
        readiness = mastery.mastery_score * 0.65 + retained * 0.25 + mastery.confidence_score * 0.10 - mistake_pressure * 0.25
        if readiness < 0.35:
            target = QuizDifficultyLevel.foundation
            complexity = "single-concept recall and recognition"
            explanation = "high detail with corrective feedback"
            reinforcement = 0.92
        elif readiness < 0.68:
            target = QuizDifficultyLevel.standard
            complexity = "concept application with familiar examples"
            explanation = "moderate detail with misconception checks"
            reinforcement = 0.68
        elif readiness < 0.86:
            target = QuizDifficultyLevel.challenge
            complexity = "transfer questions and multi-step reasoning"
            explanation = "concise rationale plus extension"
            reinforcement = 0.38
        else:
            target = QuizDifficultyLevel.exam_ready
            complexity = "exam-style synthesis and edge cases"
            explanation = "brief expert feedback"
            reinforcement = 0.22
        return QuizDifficultyDecision(
            learner_id=learner_id,
            concept_id=mastery.concept_id,
            target_difficulty=target,
            question_complexity=complexity,
            explanation_depth=explanation,
            challenge_level=max(0.0, min(1.0, readiness)),
            reinforcement_intensity=reinforcement,
            rationale=f"Readiness={readiness:.2f}, mastery={mastery.mastery_score:.2f}, retained={retained:.2f}, mistakes={mistake_pressure:.2f}.",
        )

    def learning_path(
        self,
        learner_id: str,
        mastery: list[ConceptMastery] | None = None,
        retention: list[RetentionSnapshot] | None = None,
    ) -> PersonalizedLearningPath:
        mastery = mastery or learner_store.list_mastery(learner_id)
        retention = retention or retention_service.snapshots_for_learner(learner_id)
        due_ids = {item.concept_id for item in retention if item.revision_due}
        sorted_mastery = sorted(mastery, key=lambda item: (item.mastery_score, item.last_studied_at is not None))
        nodes: list[LearningPathNode] = []
        for index, item in enumerate(sorted_mastery):
            prerequisites = [prev.concept_id for prev in sorted_mastery[:index] if prev.mastery_score < 0.7]
            if item.concept_id in due_ids:
                action = LearningPathAction.pause_for_review
                rationale = "Retention review is due before moving forward."
            elif prerequisites:
                action = LearningPathAction.revise_prerequisite
                rationale = "Earlier weak concepts should be repaired before this topic."
            elif item.mastery_score >= 0.82:
                action = LearningPathAction.unlock_next_topic
                rationale = "Mastery gate is passed; learner can progress."
            elif item.mastery_score >= 0.62:
                action = LearningPathAction.consolidate_mastery
                rationale = "Learner is close to proficiency and should consolidate."
            else:
                action = LearningPathAction.continue_current
                rationale = "Concept needs more guided practice."
            nodes.append(
                LearningPathNode(
                    concept_id=item.concept_id,
                    concept_name=item.concept_name,
                    sequence_index=index,
                    action=action,
                    unlocked=not prerequisites,
                    prerequisite_concept_ids=prerequisites,
                    rationale=rationale,
                )
            )
        next_action = nodes[0].action if nodes else LearningPathAction.continue_current
        return PersonalizedLearningPath(learner_id=learner_id, nodes=nodes, next_action=next_action, rationale="Path is sorted by weakest mastery and revision urgency.")

    def revision_priorities(
        self,
        learner_id: str,
        mastery: list[ConceptMastery] | None = None,
        retention: list[RetentionSnapshot] | None = None,
    ) -> list[RevisionDecision]:
        mastery = mastery or learner_store.list_mastery(learner_id)
        retention = retention or retention_service.snapshots_for_learner(learner_id)
        mastery_map = {item.concept_id: item for item in mastery}
        decisions: list[RevisionDecision] = []
        for snapshot in retention:
            item = mastery_map.get(snapshot.concept_id)
            confusion = min(0.25, (item.confusion_count if item else 0) * 0.06)
            urgency = (1 - snapshot.retained_score) * 0.62 + (0.22 if snapshot.revision_due else 0) + confusion
            hours = 4 if urgency >= 0.82 else 12 if urgency >= 0.65 else 48 if urgency >= 0.42 else 120
            decisions.append(
                RevisionDecision(
                    learner_id=learner_id,
                    concept_id=snapshot.concept_id,
                    urgency_score=max(0.0, min(1.0, urgency)),
                    retained_score=snapshot.retained_score,
                    due_now=snapshot.revision_due,
                    recommended_interval_hours=hours,
                    rationale="Urgency combines retention decay, due status, and confusion pressure.",
                )
            )
        return sorted(decisions, key=lambda item: item.urgency_score, reverse=True)

    def cognitive_load(self, learner_id: str, sessions: list[StudySession] | None = None) -> CognitiveLoadSnapshot:
        sessions = sessions if sessions is not None else [session for session in learner_store.list_sessions(learner_id) if session.ended_at is None]
        if not sessions:
            return CognitiveLoadSnapshot(
                learner_id=learner_id,
                fatigue_score=0.12,
                load_level=CognitiveLoadLevel.low,
                overload_detected=False,
                pacing_adjustment="normal",
                contributing_signals=["no active study session"],
            )
        latest = sorted(sessions, key=lambda item: item.started_at)[-1]
        event_total = sum(latest.event_counts.values())
        low_accuracy = 1 - latest.quiz_accuracy if latest.quiz_attempts else 0
        duration_pressure = min(1.0, latest.duration_seconds / 3600)
        interaction_pressure = min(1.0, event_total / 24)
        fatigue = min(1.0, duration_pressure * 0.34 + interaction_pressure * 0.28 + low_accuracy * 0.28 + (1 - latest.engagement_score) * 0.10)
        if fatigue >= 0.78:
            level = CognitiveLoadLevel.overload
            pacing = "slow_down_with_short_steps"
        elif fatigue >= 0.58:
            level = CognitiveLoadLevel.elevated
            pacing = "reduce_challenge_and_add_checks"
        elif fatigue >= 0.32:
            level = CognitiveLoadLevel.balanced
            pacing = "maintain_with_periodic_reflection"
        else:
            level = CognitiveLoadLevel.low
            pacing = "normal"
        signals = [
            f"duration_pressure={duration_pressure:.2f}",
            f"interaction_pressure={interaction_pressure:.2f}",
            f"low_accuracy={low_accuracy:.2f}",
            f"engagement={latest.engagement_score:.2f}",
        ]
        return CognitiveLoadSnapshot(
            learner_id=learner_id,
            fatigue_score=fatigue,
            load_level=level,
            overload_detected=level == CognitiveLoadLevel.overload,
            pacing_adjustment=pacing,
            contributing_signals=signals,
        )

    def _select_mastery(self, mastery: list[ConceptMastery], concept_id: str | None) -> ConceptMastery | None:
        if concept_id:
            return next((item for item in mastery if item.concept_id == concept_id), None)
        return sorted(mastery, key=lambda item: item.mastery_score)[0] if mastery else None

    def _mode_directives(self, mode: TutoringMode) -> list[str]:
        return {
            TutoringMode.beginner: ["Define terms first.", "Use simple examples.", "Check understanding after each idea."],
            TutoringMode.concise: ["Answer directly.", "Avoid unnecessary background.", "Give one next step."],
            TutoringMode.deep_explanation: ["Explain causal reasoning.", "Use examples and counterexamples.", "Surface misconceptions."],
            TutoringMode.exam_preparation: ["Use exam framing.", "Include transfer questions.", "Emphasize common traps."],
            TutoringMode.step_by_step: ["Break into small steps.", "Wait for learner confirmation.", "Repair one misconception at a time."],
            TutoringMode.visual_conceptual: ["Describe a mental model.", "Use spatial or diagram-like language.", "Connect parts to whole."],
        }[mode]

    def _explanation_depth(self, mode: TutoringMode) -> str:
        return {
            TutoringMode.beginner: "foundational",
            TutoringMode.concise: "brief",
            TutoringMode.deep_explanation: "deep",
            TutoringMode.exam_preparation: "exam-focused",
            TutoringMode.step_by_step: "guided",
            TutoringMode.visual_conceptual: "conceptual",
        }[mode]

    def _interaction_style(self, mode: TutoringMode) -> str:
        return {
            TutoringMode.beginner: "scaffolded",
            TutoringMode.concise: "direct",
            TutoringMode.deep_explanation: "socratic with examples",
            TutoringMode.exam_preparation: "challenge-oriented",
            TutoringMode.step_by_step: "paced coaching",
            TutoringMode.visual_conceptual: "analogy and mental model",
        }[mode]


adaptive_decision_engine = AdaptiveDecisionEngine()

