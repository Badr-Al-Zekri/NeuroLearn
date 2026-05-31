from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def upload_text() -> str:
    response = client.post(
        "/api/documents/upload",
        data={
            "title": "Learning science",
            "text": "Active recall helps learners strengthen memory. Spaced repetition improves long term retention. Feedback helps students correct mistakes and focus future study sessions.",
        },
    )
    assert response.status_code == 200
    return response.json()["document_id"]


def test_health_uses_mock_mode_without_key():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["ai_mode"] in {"mock", "gemini"}
    assert body["embedding_provider"]
    assert body["vector_store_provider"]


def test_upload_requires_content():
    response = client.post("/api/documents/upload", data={"title": "Empty"})
    assert response.status_code == 400


def test_text_upload_and_get_document():
    document_id = upload_text()
    response = client.get(f"/api/documents/{document_id}")
    assert response.status_code == 200
    assert response.json()["features"]["summary"] is True
    assert response.json()["features"]["rag"] is True
    assert response.json()["chunk_count"] > 0


def test_missing_document_returns_404():
    response = client.get("/api/documents/missing")
    assert response.status_code == 404


def test_mock_summary_quiz_and_chat():
    document_id = upload_text()

    summary = client.post(f"/api/documents/{document_id}/summary", json={})
    assert summary.status_code == 200
    assert len(summary.json()["key_insights"]) >= 3

    quiz = client.post(f"/api/documents/{document_id}/quiz", json={"question_count": 3})
    assert quiz.status_code == 200
    assert len(quiz.json()["questions"]) == 3

    chat = client.post(f"/api/documents/{document_id}/chat", json={"message": "What should I study first?"})
    assert chat.status_code == 200
    assert chat.json()["answer"]
    assert "source_chunks" in chat.json()


def test_retrieval_and_knowledge_endpoints():
    document_id = upload_text()

    retrieval = client.post(f"/api/documents/{document_id}/retrieve", json={"query": "active recall retention", "top_k": 3})
    assert retrieval.status_code == 200
    assert retrieval.json()["chunks"]

    knowledge = client.get(f"/api/documents/{document_id}/knowledge")
    assert knowledge.status_code == 200
    assert knowledge.json()["study_metadata"]["chunk_count"] > 0
    assert knowledge.json()["study_metadata"]["objective_count"] > 0
    assert knowledge.json()["study_metadata"]["relationship_count"] > 0
