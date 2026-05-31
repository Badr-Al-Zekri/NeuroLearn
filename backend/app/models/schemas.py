from datetime import datetime
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field


class DocumentKind(str, Enum):
    text = "text"
    pdf = "pdf"


class DifficultyLevel(str, Enum):
    introductory = "introductory"
    intermediate = "intermediate"
    advanced = "advanced"


class RelationshipType(str, Enum):
    prerequisite = "prerequisite"
    supports = "supports"
    contrasts = "contrasts"
    applies_to = "applies_to"
    assessed_by = "assessed_by"


class Concept(BaseModel):
    concept_id: str
    name: str
    description: str
    difficulty: DifficultyLevel = DifficultyLevel.introductory
    aliases: list[str] = Field(default_factory=list)
    related_concepts: list[str] = Field(default_factory=list)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class LearningObjective(BaseModel):
    objective_id: str
    document_id: str
    description: str
    concept_ids: list[str] = Field(default_factory=list)
    bloom_level: Literal["remember", "understand", "apply", "analyze", "evaluate", "create"] = "understand"
    difficulty: DifficultyLevel = DifficultyLevel.introductory
    evidence_chunk_ids: list[str] = Field(default_factory=list)


class KnowledgeRelationship(BaseModel):
    relationship_id: str
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    strength: float = Field(default=0.5, ge=0, le=1)
    rationale: str = ""
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class LearningSession(BaseModel):
    session_id: str
    learner_id: str = "demo-learner"
    document_ids: list[str] = Field(default_factory=list)
    active_objective_ids: list[str] = Field(default_factory=list)
    mastered_concept_ids: list[str] = Field(default_factory=list)
    struggling_concept_ids: list[str] = Field(default_factory=list)
    retrieval_history: list[str] = Field(default_factory=list)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class DocumentRecord(BaseModel):
    document_id: str
    title: str
    kind: DocumentKind
    content: str
    word_count: int
    created_at: datetime
    chunk_count: int = 0
    concepts: list[Concept] = Field(default_factory=list)
    topics: list["LearningTopic"] = Field(default_factory=list)
    learning_objectives: list[LearningObjective] = Field(default_factory=list)
    relationships: list[KnowledgeRelationship] = Field(default_factory=list)


class DocumentResponse(BaseModel):
    document_id: str
    title: str
    kind: DocumentKind
    word_count: int
    chunk_count: int = 0
    created_at: datetime
    features: dict[str, bool] = Field(default_factory=dict)


class TextUploadRequest(BaseModel):
    title: str = Field(default="Untitled notes", max_length=120)
    text: str = Field(min_length=20)


class HealthResponse(BaseModel):
    status: Literal["ok"]
    app_name: str
    version: str
    ai_mode: Literal["mock", "gemini"]
    embedding_provider: str
    vector_store_provider: str


class SummaryRequest(BaseModel):
    tone: str = Field(default="clear and student-friendly", max_length=80)


class SummaryResponse(BaseModel):
    title: str
    overview: str
    key_insights: list[str] = Field(min_length=3)
    study_actions: list[str] = Field(min_length=3)
    confidence: float = Field(ge=0, le=1)
    source_coverage: str


class QuizRequest(BaseModel):
    question_count: int = Field(default=5, ge=3, le=10)
    difficulty: Literal["mixed", "easy", "medium", "hard"] = "mixed"


class QuizQuestion(BaseModel):
    id: str
    question: str
    options: list[str] = Field(min_length=4, max_length=4)
    correct_index: int = Field(ge=0, le=3)
    explanation: str
    difficulty: Literal["easy", "medium", "hard"]


class QuizResponse(BaseModel):
    title: str
    questions: list[QuizQuestion]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=1200)
    history: list[ChatMessage] = Field(default_factory=list, max_length=12)


class ChatResponse(BaseModel):
    answer: str
    cited_insights: list[str] = Field(default_factory=list)
    source_chunks: list["RetrievedChunk"] = Field(default_factory=list)


class KnowledgeChunkMetadata(BaseModel):
    document_id: str
    title: str
    chunk_index: int
    heading: str | None = None
    section_path: list[str] = Field(default_factory=list)
    source_kind: DocumentKind
    word_count: int
    token_estimate: int
    topics: list[str] = Field(default_factory=list)
    concepts: list[str] = Field(default_factory=list)
    learning_objective_ids: list[str] = Field(default_factory=list)
    difficulty: DifficultyLevel = DifficultyLevel.introductory
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class KnowledgeChunk(BaseModel):
    chunk_id: str
    text: str
    metadata: KnowledgeChunkMetadata


class ProcessedDocument(BaseModel):
    document_id: str
    title: str
    kind: DocumentKind
    normalized_text: str
    chunks: list[KnowledgeChunk]
    concepts: list[Concept] = Field(default_factory=list)
    topics: list["LearningTopic"] = Field(default_factory=list)
    learning_objectives: list[LearningObjective] = Field(default_factory=list)
    relationships: list[KnowledgeRelationship] = Field(default_factory=list)


class EmbeddingVector(BaseModel):
    text_id: str
    values: list[float]
    provider: str = "mock"
    model: str = "mock-hash"
    dimensions: int = 0
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    chunk_id: str
    text: str
    score: float
    metadata: KnowledgeChunkMetadata


class RetrievalRequest(BaseModel):
    query: str = Field(min_length=2, max_length=1200)
    top_k: int = Field(default=6, ge=1, le=12)
    topics: list[str] = Field(default_factory=list)
    difficulty: Literal["any", "introductory", "intermediate", "advanced"] = "any"


class RetrievalResponse(BaseModel):
    query: str
    chunks: list[RetrievedChunk]


LearningConcept = Concept
ChunkMetadata = KnowledgeChunkMetadata
DocumentChunk = KnowledgeChunk
Document = DocumentRecord


class LearningTopic(BaseModel):
    topic_id: str
    name: str
    summary: str
    concept_ids: list[str] = Field(default_factory=list)
    prerequisite_topic_ids: list[str] = Field(default_factory=list)


class StudyMetadata(BaseModel):
    document_id: str
    estimated_reading_minutes: int
    difficulty: DifficultyLevel
    primary_topics: list[str]
    concept_count: int
    chunk_count: int


class TutorMemory(BaseModel):
    learner_id: str = "demo-learner"
    mastered_concepts: list[str] = Field(default_factory=list)
    struggling_concepts: list[str] = Field(default_factory=list)
    preferred_explanation_style: str = "clear, concrete, and example-driven"
    recent_goals: list[str] = Field(default_factory=list)


class LearningAnalyticsSnapshot(BaseModel):
    document_id: str
    retrieval_count: int = 0
    chat_turns: int = 0
    quiz_attempts: int = 0
    weak_topics: list[str] = Field(default_factory=list)


class ApiError(BaseModel):
    detail: str
