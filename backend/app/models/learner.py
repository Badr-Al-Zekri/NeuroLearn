from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class MasteryStatus(str, Enum):
    unseen = "unseen"
    learning = "learning"
    developing = "developing"
    proficient = "proficient"
    mastered = "mastered"
    needs_revision = "needs_revision"


class StudyEventType(str, Enum):
    document_view = "document_view"
    retrieval = "retrieval"
    chat = "chat"
    quiz_attempt = "quiz_attempt"
    revision = "revision"
    recommendation_click = "recommendation_click"


class RecommendationType(str, Enum):
    revise_weak_concept = "revise_weak_concept"
    practice_quiz = "practice_quiz"
    next_topic = "next_topic"
    tutoring_prompt = "tutoring_prompt"
    retention_review = "retention_review"


class LearnerProfile(BaseModel):
    learner_id: str
    display_name: str = "Demo Learner"
    academic_level: str = "university"
    preferred_explanation_style: str = "clear, concrete, and example-driven"
    goals: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class MasteryObservation(BaseModel):
    observed_at: datetime
    source: StudyEventType
    delta: float
    score_after: float
    evidence: str = ""


class ConceptMastery(BaseModel):
    learner_id: str
    concept_id: str
    concept_name: str
    mastery_score: float = Field(default=0.0, ge=0, le=1)
    confidence_score: float = Field(default=0.0, ge=0, le=1)
    quiz_attempts: int = 0
    quiz_correct: int = 0
    confusion_count: int = 0
    revision_count: int = 0
    last_studied_at: datetime | None = None
    next_review_at: datetime | None = None
    status: MasteryStatus = MasteryStatus.unseen
    observations: list[MasteryObservation] = Field(default_factory=list)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class LearningMemory(BaseModel):
    learner_id: str
    studied_concept_ids: list[str] = Field(default_factory=list)
    failed_concept_ids: list[str] = Field(default_factory=list)
    repeated_mistakes: dict[str, int] = Field(default_factory=dict)
    learning_history: list[str] = Field(default_factory=list)
    revision_history: list[str] = Field(default_factory=list)
    session_ids: list[str] = Field(default_factory=list)
    updated_at: datetime


class StudySession(BaseModel):
    session_id: str
    learner_id: str
    document_ids: list[str] = Field(default_factory=list)
    started_at: datetime
    ended_at: datetime | None = None
    duration_seconds: int = 0
    event_counts: dict[str, int] = Field(default_factory=dict)
    quiz_attempts: int = 0
    quiz_accuracy: float = 0.0
    retrieval_interactions: int = 0
    chat_turns: int = 0
    topic_difficulty_trends: dict[str, float] = Field(default_factory=dict)
    engagement_score: float = Field(default=0.0, ge=0, le=1)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class RetentionSnapshot(BaseModel):
    learner_id: str
    concept_id: str
    retained_score: float = Field(ge=0, le=1)
    decay_factor: float = Field(ge=0, le=1)
    days_since_review: float
    revision_due: bool
    next_review_at: datetime
    generated_at: datetime


class WeaknessProfile(BaseModel):
    learner_id: str
    weak_concept_ids: list[str] = Field(default_factory=list)
    confusion_indicators: dict[str, int] = Field(default_factory=dict)
    low_accuracy_concepts: list[str] = Field(default_factory=list)
    revision_needed_concepts: list[str] = Field(default_factory=list)
    generated_at: datetime


class RecommendationItem(BaseModel):
    recommendation_id: str
    recommendation_type: RecommendationType
    title: str
    rationale: str
    concept_id: str | None = None
    priority: float = Field(default=0.5, ge=0, le=1)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class RecommendationProfile(BaseModel):
    learner_id: str
    recommendations: list[RecommendationItem] = Field(default_factory=list)
    generated_at: datetime


class QuizResultEvent(BaseModel):
    concept_id: str
    concept_name: str
    correct: bool
    confidence: float = Field(default=0.5, ge=0, le=1)
    confusion_signal: bool = False
    evidence: str = ""


class StudyEventRequest(BaseModel):
    event_type: StudyEventType
    concept_id: str | None = None
    concept_name: str | None = None
    document_id: str | None = None
    correct: bool | None = None
    confidence: float = Field(default=0.5, ge=0, le=1)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class LearnerIntelligenceSnapshot(BaseModel):
    profile: LearnerProfile
    memory: LearningMemory
    mastery: list[ConceptMastery]
    weakness_profile: WeaknessProfile
    recommendations: RecommendationProfile
    retention: list[RetentionSnapshot]
    active_sessions: list[StudySession]

