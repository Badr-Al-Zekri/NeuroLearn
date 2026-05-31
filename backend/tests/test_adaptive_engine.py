from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def seed_quiz_result(learner_id: str, concept_id: str, correct: bool, confidence: float = 0.6, confusion: bool = False):
    response = client.post(
        f"/api/learners/{learner_id}/mastery/quiz-result",
        json={
            "concept_id": concept_id,
            "concept_name": concept_id.replace("-", " ").title(),
            "correct": correct,
            "confidence": confidence,
            "confusion_signal": confusion,
            "evidence": "adaptive test seed",
        },
    )
    assert response.status_code == 200
    return response.json()


def test_adaptive_decision_ranks_revision_and_selects_tutoring_mode():
    learner_id = "adaptive-student"
    seed_quiz_result(learner_id, "active-recall", False, confidence=0.9, confusion=True)
    seed_quiz_result(learner_id, "spaced-repetition", True, confidence=0.8)

    response = client.get(f"/api/learners/{learner_id}/adaptive/decision?concept_id=active-recall")
    assert response.status_code == 200
    body = response.json()
    assert body["tutoring_strategy"]["mode"] in {"beginner", "step_by_step"}
    assert body["quiz_difficulty"]["target_difficulty"] == "foundation"
    assert body["revision_priorities"]
    assert body["learning_path"]["nodes"]
    assert body["explainability"]


def test_adaptive_quiz_difficulty_increases_with_mastery():
    learner_id = "challenge-student"
    for _ in range(6):
        seed_quiz_result(learner_id, "retrieval-practice", True, confidence=0.95)

    response = client.get(f"/api/learners/{learner_id}/adaptive/quiz-difficulty/retrieval-practice")
    assert response.status_code == 200
    body = response.json()
    assert body["target_difficulty"] in {"challenge", "exam_ready"}
    assert body["challenge_level"] > 0.65


def test_cognitive_load_reflects_active_session_activity():
    learner_id = "load-student"
    session = client.post(f"/api/learners/{learner_id}/sessions", json={"document_ids": ["doc-load"]})
    assert session.status_code == 200
    session_id = session.json()["session_id"]

    for index in range(6):
        event = client.post(
            f"/api/learners/{learner_id}/sessions/{session_id}/events",
            json={
                "event_type": "quiz_attempt",
                "concept_id": f"concept-{index}",
                "concept_name": f"Concept {index}",
                "correct": False,
                "confidence": 0.7,
            },
        )
        assert event.status_code == 200

    load = client.get(f"/api/learners/{learner_id}/adaptive/cognitive-load")
    assert load.status_code == 200
    body = load.json()
    assert body["fatigue_score"] > 0
    assert body["pacing_adjustment"] in {
        "normal",
        "maintain_with_periodic_reflection",
        "reduce_challenge_and_add_checks",
        "slow_down_with_short_steps",
    }


def test_adaptive_learning_path_endpoint_handles_empty_and_seeded_states():
    empty = client.get("/api/learners/path-empty/adaptive/learning-path")
    assert empty.status_code == 200
    assert empty.json()["nodes"] == []

    learner_id = "path-student"
    seed_quiz_result(learner_id, "foundation-topic", False, confidence=0.8, confusion=True)
    seed_quiz_result(learner_id, "advanced-topic", True, confidence=0.9)

    path = client.get(f"/api/learners/{learner_id}/adaptive/learning-path")
    assert path.status_code == 200
    assert len(path.json()["nodes"]) >= 2
    assert path.json()["next_action"] in {
        "continue_current",
        "revise_prerequisite",
        "pause_for_review",
        "consolidate_mastery",
        "unlock_next_topic",
    }

