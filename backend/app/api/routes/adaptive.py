from fastapi import APIRouter, Query
from app.models.adaptive import (
    AdaptiveDecision,
    CognitiveLoadSnapshot,
    PersonalizedLearningPath,
    QuizDifficultyDecision,
    RevisionDecision,
    TutoringStrategy,
)
from app.services.adaptive_engine import adaptive_decision_engine
from app.services.learner_store import learner_store

router = APIRouter(prefix="/api/learners/{learner_id}/adaptive", tags=["adaptive"])


@router.get("/decision", response_model=AdaptiveDecision)
async def get_adaptive_decision(learner_id: str, concept_id: str | None = Query(default=None)) -> AdaptiveDecision:
    learner_store.get_or_create_profile(learner_id)
    return adaptive_decision_engine.decision(learner_id, concept_id)


@router.get("/learning-path", response_model=PersonalizedLearningPath)
async def get_learning_path(learner_id: str) -> PersonalizedLearningPath:
    learner_store.get_or_create_profile(learner_id)
    return adaptive_decision_engine.learning_path(learner_id)


@router.get("/quiz-difficulty/{concept_id}", response_model=QuizDifficultyDecision)
async def get_quiz_difficulty(learner_id: str, concept_id: str) -> QuizDifficultyDecision:
    learner_store.get_or_create_profile(learner_id)
    mastery = learner_store.get_mastery(learner_id, concept_id, concept_id.replace("-", " ").title())
    return adaptive_decision_engine.quiz_difficulty(learner_id, mastery)


@router.get("/revision-priorities", response_model=list[RevisionDecision])
async def get_revision_priorities(learner_id: str) -> list[RevisionDecision]:
    learner_store.get_or_create_profile(learner_id)
    return adaptive_decision_engine.revision_priorities(learner_id)


@router.get("/cognitive-load", response_model=CognitiveLoadSnapshot)
async def get_cognitive_load(learner_id: str) -> CognitiveLoadSnapshot:
    learner_store.get_or_create_profile(learner_id)
    return adaptive_decision_engine.cognitive_load(learner_id)


@router.get("/tutoring-mode", response_model=TutoringStrategy)
async def get_tutoring_mode(learner_id: str, concept_id: str | None = Query(default=None)) -> TutoringStrategy:
    learner_store.get_or_create_profile(learner_id)
    if concept_id:
        mastery = learner_store.get_mastery(learner_id, concept_id, concept_id.replace("-", " ").title())
    else:
        mastery_items = learner_store.list_mastery(learner_id)
        mastery = sorted(mastery_items, key=lambda item: item.mastery_score)[0] if mastery_items else None
    return adaptive_decision_engine.tutoring_strategy(learner_id, mastery)

