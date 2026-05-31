from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_learner_profile_and_empty_intelligence_snapshot():
    response = client.get("/api/learners/demo-student/profile")
    assert response.status_code == 200
    assert response.json()["learner_id"] == "demo-student"

    snapshot = client.get("/api/learners/demo-student/intelligence")
    assert snapshot.status_code == 200
    body = snapshot.json()
    assert body["memory"]["learner_id"] == "demo-student"
    assert body["mastery"] == []


def test_quiz_result_updates_mastery_memory_retention_and_recommendations():
    learner_id = "quiz-student"
    result = client.post(
        f"/api/learners/{learner_id}/mastery/quiz-result",
        json={
            "concept_id": "active-recall",
            "concept_name": "Active Recall",
            "correct": False,
            "confidence": 0.8,
            "confusion_signal": True,
            "evidence": "Chose rereading instead of retrieval practice.",
        },
    )
    assert result.status_code == 200
    assert result.json()["mastery_score"] < 0.5

    memory = client.get(f"/api/learners/{learner_id}/memory")
    assert memory.status_code == 200
    assert "active-recall" in memory.json()["studied_concept_ids"]

    weakness = client.get(f"/api/learners/{learner_id}/weakness-profile")
    assert weakness.status_code == 200
    assert "active-recall" in weakness.json()["weak_concept_ids"]

    retention = client.get(f"/api/learners/{learner_id}/retention")
    assert retention.status_code == 200
    assert retention.json()[0]["concept_id"] == "active-recall"

    recommendations = client.get(f"/api/learners/{learner_id}/recommendations")
    assert recommendations.status_code == 200
    assert recommendations.json()["recommendations"]


def test_study_session_records_events_and_engagement():
    learner_id = "session-student"
    session = client.post(f"/api/learners/{learner_id}/sessions", json={"document_ids": ["doc-1"]})
    assert session.status_code == 200
    session_id = session.json()["session_id"]

    event = client.post(
        f"/api/learners/{learner_id}/sessions/{session_id}/events",
        json={
            "event_type": "quiz_attempt",
            "concept_id": "spacing",
            "concept_name": "Spaced Repetition",
            "correct": True,
            "confidence": 0.9,
        },
    )
    assert event.status_code == 200
    body = event.json()
    assert body["quiz_attempts"] == 1
    assert body["quiz_accuracy"] == 1.0
    assert body["engagement_score"] > 0

    ended = client.post(f"/api/learners/{learner_id}/sessions/{session_id}/end")
    assert ended.status_code == 200
    assert ended.json()["ended_at"] is not None

