# NeuroLearn AI

NeuroLearn AI is a demo-ready educational AI platform with a Flutter Web frontend and a FastAPI backend. Users can upload readable PDFs or paste text, then generate summaries, key insights, quizzes, and document-grounded chat responses.

## Architecture

- `frontend/` contains the Flutter Web app with Riverpod state, feature-first screens, shared models, and reusable UI widgets.
- `backend/` contains the FastAPI API, Pydantic schemas, document upload flow, in-memory document store, PDF text extraction, prompt templates, and AI client abstraction.
- The backend uses Gemini when `GEMINI_API_KEY` is set. Without a key, it runs in deterministic mock mode so the full product demo still works.
- `backend/AI_LEARNING_ARCHITECTURE.md` documents the new document processing, embedding, vector search, RAG, knowledge modeling, and tutor foundation.

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Endpoints:

- `GET /health`
- `POST /api/documents/upload`
- `GET /api/documents/{document_id}`
- `GET /api/documents/{document_id}/knowledge`
- `POST /api/documents/{document_id}/retrieve`
- `POST /api/documents/{document_id}/summary`
- `POST /api/documents/{document_id}/quiz`
- `POST /api/documents/{document_id}/chat`
- `GET /api/learners/{learner_id}/profile`
- `POST /api/learners/{learner_id}/sessions`
- `POST /api/learners/{learner_id}/sessions/{session_id}/events`
- `POST /api/learners/{learner_id}/mastery/quiz-result`
- `GET /api/learners/{learner_id}/intelligence`
- `GET /api/learners/{learner_id}/recommendations`
- `GET /api/learners/{learner_id}/retention`
- `GET /api/learners/{learner_id}/adaptive/decision`
- `GET /api/learners/{learner_id}/adaptive/learning-path`
- `GET /api/learners/{learner_id}/adaptive/quiz-difficulty/{concept_id}`
- `GET /api/learners/{learner_id}/adaptive/revision-priorities`
- `GET /api/learners/{learner_id}/adaptive/cognitive-load`
- `GET /api/learners/{learner_id}/adaptive/tutoring-mode`

Optional Qdrant mode:

```bash
set VECTOR_STORE_PROVIDER=qdrant
set QDRANT_URL=http://localhost:6333
set QDRANT_COLLECTION=neurolearn_chunks
```

## Frontend

```bash
cd frontend
flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
```

The current frontend is the Learning Core MVP: a calm daily learning companion built around four primary experiences.

- `Today`: homepage for what to study now, why it matters, estimated focus time, and the continue-session action.
- `Tutor`: a grounded, guided explanation space with contextual next steps after the learner has engaged.
- `Practice`: a short, one-question-at-a-time review that withholds scoring pressure until completion.
- `Progress`: a lightweight momentum view showing streak, sessions, ideas reviewed, gentle weak-area reminders, and a clear session completion action.

The UI intentionally avoids analytics-heavy dashboards and AI feature sprawl. It favors fast task completion, low cognitive load, and perceived learning progress.

Frontend architecture:

- Feature-first screens live under `lib/features`.
- Shared product state lives in `lib/shared/providers`.
- API integration remains centralized in `lib/core/api/api_client.dart`.
- Lightweight telemetry hooks track session start, session completion, quiz completion, successful tutor engagement, session duration, return-session detection, and material-change drop-off points in memory.
- Existing backend learner/session endpoints are used for durable MVP learning signals.

Experience principles:

- Today presents one recommended learning action and explains what follows.
- Tutor frames conversation as source-grounded study, with gentle follow-ups instead of tool controls.
- Practice shows one question at a time with immediate, supportive feedback.
- Progress closes the loop with simple momentum cues and a clear session completion moment.
- Mobile uses thumb-friendly navigation and constrained reading widths; motion stays subtle and functional.

Experience Calibration refinements:

- Today keeps a single dominant action and uses immediate, reassuring guidance rather than waiting on additional recommendation content.
- Tutor prompts frame conversation as learning continuation, with the review handoff appearing only after an explanation has begun.
- Practice acknowledges each answered step without exposing live correctness, reducing evaluation anxiety while preserving feedback.
- Progress switches from analytical labels to everyday language and stacks its momentum cues comfortably on narrow screens.
- Empty and loading states use quieter language and motion so waiting or starting without material does not feel like failure.

MVP Validation Preparation refinements:

- Replacing material clears the prior tutor conversation and session context; an unfinished replaced session records one invisible drop-off point.
- Tutor engagement is counted only when an explanation is delivered, and a bookkeeping failure never blocks the learner from continuing.
- Practice records completion when the learner finishes the review, while temporary answer-recording failures do not create a dead end.
- Progress always leaves the session completion action available, even while the momentum summary is loading or unavailable.
- Material selection disables premature text submission, blocks duplicate PDF submission while loading, and offers a clear mobile return path.

## Verification

```bash
cd backend
pytest

cd ../frontend
flutter analyze
flutter test
```

PDF uploads support extractable text. Scanned-image PDFs return a friendly unsupported-content error in this v1 demo.
