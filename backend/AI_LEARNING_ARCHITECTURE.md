# NeuroLearn AI Learning Infrastructure

This phase moves NeuroLearn AI from document summarization toward a retrieval-augmented university learning engine.

## Processing Pipeline

Uploads flow through `LearningOrchestrator`:

1. Extract source text from PDF or text input.
2. Clean noisy whitespace, page-number artifacts, and invalid characters.
3. Normalize text into stable paragraphs.
4. Build semantic chunks with overlap for retrieval continuity.
5. Enrich every chunk with document id, title, heading, topics, concepts, word count, token estimate, source kind, and difficulty.
6. Build first-pass knowledge objects: concepts, topic clusters, study metadata, and analytics seed data.

## Core Domain Model

The backend now treats learning artifacts as domain objects, not just API payloads.

- `Document` owns the canonical source text, source type, ingestion timestamps, generated knowledge objects, and feature readiness.
- `KnowledgeChunk` owns a retrieval-ready educational slice of a document. It preserves section path, heading, token estimate, concepts, topics, learning objective ids, difficulty, and source metadata.
- `Concept` represents a reusable unit of understanding with aliases, difficulty, relationship hooks, and future mastery metadata.
- `LearningObjective` describes what a learner should be able to explain, apply, or analyze after studying related concepts and chunks.
- `KnowledgeRelationship` links concepts and objectives through prerequisite, support, contrast, application, or assessment relationships.
- `LearningSession` is the future personalization boundary for active objectives, mastered/struggling concepts, retrieval history, learner goals, and analytics.

Scalability direction:

- Keep generated domain objects appendable and versionable so improved extraction models can reprocess documents without breaking old sessions.
- Store chunk payloads and knowledge graph entities separately once Postgres is introduced.
- Treat relationships as graph edges that can later move to a graph database or Postgres adjacency tables.
- Keep learner memory scoped to sessions first, then promote stable preferences and mastery signals to user-level profiles after authentication exists.

## Embeddings And Vector Storage

`EmbeddingService` owns embedding generation and supports:

- `mock` provider for deterministic local vectors.
- `gemini` provider using `gemini-embedding-001` batch embedding calls when configured.
- Configurable dimensions and batch size.

`VectorStore` owns persistence and retrieval:

- `InMemoryVectorStore` is the default local/demo backend.
- `QdrantVectorStore` is selected with `VECTOR_STORE_PROVIDER=qdrant`.
- Qdrant collection defaults to `neurolearn_chunks`, cosine distance, and payload metadata for filtering by document, topic, and difficulty.

## RAG Runtime

Runtime retrieval is split into focused services:

- `RetrieverService` embeds queries, searches vectors, applies metadata filters, and adds a lightweight lexical reranking bonus.
- `ContextBuilder` assembles compact context blocks with chunk headings and similarity scores.
- `RagService` powers grounded chat by retrieving relevant chunks, building context, and calling the AI client with only grounded source context.
- `ReasoningLayer` determines tutoring intent and response strategy before model generation.
- `AIOrchestrator` coordinates reasoning, prompt/client invocation, and validation.
- `ResponseValidationService` validates structured model output and rejects empty grounded answers.

Existing endpoints remain stable, with these additions:

- `POST /api/documents/{document_id}/retrieve`
- `GET /api/documents/{document_id}/knowledge`
- `POST /api/documents/{document_id}/chat` now returns `source_chunks`.

## Knowledge And Tutor Foundation

The current knowledge model is intentionally lightweight but future-ready:

- `LearningConcept` tracks names, descriptions, aliases, related concepts, and difficulty.
- `LearningTopic` groups concepts and can later express prerequisites.
- `StudyMetadata` captures reading effort, document difficulty, topics, concept count, and chunk count.
- `TutorMemory` prepares for learner profile, mastered concepts, weak concepts, explanation style, and goals.
- `LearningAnalyticsSnapshot` prepares for quiz attempts, retrieval count, chat turns, and weak-topic tracking.

## Learner Intelligence Foundation

The learner layer models adaptive learning signals separately from documents and retrieval.

- `LearnerProfile` owns learner identity, academic level, goals, explanation preference, and extensible metadata.
- `ConceptMastery` tracks concept understanding with mastery score, confidence score, quiz accuracy, confusion count, revision count, observations, and next review time.
- `LearningMemory` preserves studied concepts, failed concepts, repeated mistakes, learning history, revision history, and session continuity.
- `StudySession` tracks duration, event counts, quiz performance, retrieval interactions, chat turns, topic difficulty trends, and engagement score.
- `RetentionSnapshot` applies concept decay modeling and marks revision due concepts for spaced repetition.
- `WeaknessProfile` aggregates low mastery, low accuracy, confusion, and revision needs.
- `RecommendationProfile` prepares next best topic, weak concept revision, adaptive quiz, retention review, and tutoring prompt recommendations.

Scoring defaults:

- Mastery score is normalized from `0.0` to `1.0`.
- Correct confident quiz attempts increase mastery fastest.
- Incorrect or confused attempts lower mastery and raise revision pressure.
- Retention decays over time using a mastery-sensitive half-life.
- Recommendations prioritize retention reviews, weak concepts, missing quiz evidence, then next-topic continuity.

## Adaptive Tutoring Foundation

The adaptive layer consumes learner intelligence signals and produces deterministic, explainable educational decisions.

- `AdaptiveDecisionEngine` ranks recommendations, selects tutoring strategy, adapts quiz difficulty, sequences learning path actions, schedules revision, and estimates cognitive load.
- `TutoringStrategy` supports beginner, concise, deep explanation, exam preparation, step-by-step, and visual/conceptual modes.
- `QuizDifficultyDecision` adapts question complexity, explanation depth, challenge level, and reinforcement intensity from mastery, retention, mistakes, and confidence.
- `PersonalizedLearningPath` models prerequisite-aware concept sequencing and mastery-gated advancement.
- `RevisionDecision` combines retention decay, due status, and confusion pressure into an urgency score.
- `CognitiveLoadSnapshot` detects fatigue and overload from duration, interaction density, quiz accuracy, and engagement.

Design constraints:

- Adaptive logic is heuristic and explainable by default.
- LLMs may consume adaptive decisions, but they do not own policy decisions.
- Policy outputs are API-visible and testable, making them replaceable by future ML/ranking models.
- The layer is analytics-ready and can later persist decisions for experimentation and outcome tracking.

Next scalable steps:

- Persist documents/chunks/knowledge entities in Postgres.
- Store learner memory and analytics per user once authentication exists.
- Add reranking models for higher retrieval precision.
- Add prerequisite graph extraction with LLM validation.
- Add adaptive quiz generation using weak concepts and previous attempts.
