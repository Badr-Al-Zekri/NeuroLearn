from enum import Enum
from pydantic import BaseModel, Field
from app.models.learner import RecommendationItem


class TutoringMode(str, Enum):
    beginner = "beginner"
    concise = "concise"
    deep_explanation = "deep_explanation"
    exam_preparation = "exam_preparation"
    step_by_step = "step_by_step"
    visual_conceptual = "visual_conceptual"


class QuizDifficultyLevel(str, Enum):
    foundation = "foundation"
    standard = "standard"
    challenge = "challenge"
    exam_ready = "exam_ready"


class CognitiveLoadLevel(str, Enum):
    low = "low"
    balanced = "balanced"
    elevated = "elevated"
    overload = "overload"


class LearningPathAction(str, Enum):
    continue_current = "continue_current"
    revise_prerequisite = "revise_prerequisite"
    unlock_next_topic = "unlock_next_topic"
    pause_for_review = "pause_for_review"
    consolidate_mastery = "consolidate_mastery"


class CognitiveLoadSnapshot(BaseModel):
    learner_id: str
    fatigue_score: float = Field(ge=0, le=1)
    load_level: CognitiveLoadLevel
    overload_detected: bool
    pacing_adjustment: str
    contributing_signals: list[str] = Field(default_factory=list)


class TutoringStrategy(BaseModel):
    learner_id: str
    concept_id: str | None = None
    mode: TutoringMode
    explanation_depth: str
    interaction_style: str
    prompt_directives: list[str]
    rationale: str


class QuizDifficultyDecision(BaseModel):
    learner_id: str
    concept_id: str
    target_difficulty: QuizDifficultyLevel
    question_complexity: str
    explanation_depth: str
    challenge_level: float = Field(ge=0, le=1)
    reinforcement_intensity: float = Field(ge=0, le=1)
    rationale: str


class RevisionDecision(BaseModel):
    learner_id: str
    concept_id: str
    urgency_score: float = Field(ge=0, le=1)
    retained_score: float = Field(ge=0, le=1)
    due_now: bool
    recommended_interval_hours: int
    rationale: str


class LearningPathNode(BaseModel):
    concept_id: str
    concept_name: str
    sequence_index: int
    action: LearningPathAction
    mastery_gate: float = Field(default=0.7, ge=0, le=1)
    unlocked: bool
    prerequisite_concept_ids: list[str] = Field(default_factory=list)
    rationale: str


class PersonalizedLearningPath(BaseModel):
    learner_id: str
    nodes: list[LearningPathNode] = Field(default_factory=list)
    next_action: LearningPathAction = LearningPathAction.continue_current
    rationale: str


class AdaptiveDecision(BaseModel):
    learner_id: str
    ranked_recommendations: list[RecommendationItem]
    tutoring_strategy: TutoringStrategy
    quiz_difficulty: QuizDifficultyDecision | None = None
    learning_path: PersonalizedLearningPath
    revision_priorities: list[RevisionDecision]
    cognitive_load: CognitiveLoadSnapshot
    explainability: list[str] = Field(default_factory=list)

