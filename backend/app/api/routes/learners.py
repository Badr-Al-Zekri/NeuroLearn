from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.models.learner import (
    ConceptMastery,
    LearnerIntelligenceSnapshot,
    LearnerProfile,
    LearningMemory,
    QuizResultEvent,
    RecommendationProfile,
    RetentionSnapshot,
    StudyEventRequest,
    StudySession,
    WeaknessProfile,
)
from app.services.learner_intelligence_service import learner_intelligence_service
from app.services.learner_store import learner_store
from app.services.recommendation_service import recommendation_service
from app.services.retention_service import retention_service
from app.services.study_session_service import study_session_service

router = APIRouter(prefix="/api/learners", tags=["learners"])


class StartSessionRequest(BaseModel):
    document_ids: list[str] = Field(default_factory=list)


@router.get("/{learner_id}/profile", response_model=LearnerProfile)
async def get_profile(learner_id: str) -> LearnerProfile:
    return learner_intelligence_service.profile(learner_id)


@router.get("/{learner_id}/memory", response_model=LearningMemory)
async def get_memory(learner_id: str) -> LearningMemory:
    learner_store.get_or_create_profile(learner_id)
    return learner_store.get_memory(learner_id)


@router.post("/{learner_id}/sessions", response_model=StudySession)
async def start_session(learner_id: str, request: StartSessionRequest) -> StudySession:
    return study_session_service.start_session(learner_id, request.document_ids)


@router.post("/{learner_id}/sessions/{session_id}/events", response_model=StudySession)
async def record_session_event(learner_id: str, session_id: str, request: StudyEventRequest) -> StudySession:
    try:
        return study_session_service.record_event(learner_id, session_id, request)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{learner_id}/sessions/{session_id}/end", response_model=StudySession)
async def end_session(learner_id: str, session_id: str) -> StudySession:
    try:
        return study_session_service.end_session(learner_id, session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{learner_id}/mastery/quiz-result")
async def record_quiz_result(learner_id: str, request: QuizResultEvent) -> ConceptMastery:
    return learner_intelligence_service.record_quiz_result(learner_id, request)


@router.get("/{learner_id}/retention", response_model=list[RetentionSnapshot])
async def get_retention(learner_id: str) -> list[RetentionSnapshot]:
    learner_store.get_or_create_profile(learner_id)
    return retention_service.snapshots_for_learner(learner_id)


@router.get("/{learner_id}/weakness-profile", response_model=WeaknessProfile)
async def get_weakness_profile(learner_id: str) -> WeaknessProfile:
    learner_store.get_or_create_profile(learner_id)
    return recommendation_service.weakness_profile(learner_id)


@router.get("/{learner_id}/recommendations", response_model=RecommendationProfile)
async def get_recommendations(learner_id: str) -> RecommendationProfile:
    learner_store.get_or_create_profile(learner_id)
    return recommendation_service.recommendations(learner_id)


@router.get("/{learner_id}/intelligence", response_model=LearnerIntelligenceSnapshot)
async def get_intelligence_snapshot(learner_id: str) -> LearnerIntelligenceSnapshot:
    return learner_intelligence_service.snapshot(learner_id)
