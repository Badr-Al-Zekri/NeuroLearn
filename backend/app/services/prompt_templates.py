from app.models.schemas import ChatMessage


def _clip(content: str, limit: int = 18000) -> str:
    return content[:limit]


class PromptTemplates:
    @staticmethod
    def summary(document_title: str, document_text: str, tone: str) -> str:
        return f"""
You are NeuroLearn AI, an expert study coach.
Create a concise study summary for the document below.
Return only valid JSON with this exact shape:
{{
  "title": "string",
  "overview": "string",
  "key_insights": ["string", "string", "string"],
  "study_actions": ["string", "string", "string"],
  "confidence": 0.0,
  "source_coverage": "string"
}}
Tone: {tone}
Document title: {document_title}
Document:
{_clip(document_text)}
""".strip()

    @staticmethod
    def quiz(document_title: str, document_text: str, question_count: int, difficulty: str) -> str:
        return f"""
You are NeuroLearn AI, an assessment designer.
Generate {question_count} multiple choice questions from the document.
Return only valid JSON with this exact shape:
{{
  "title": "string",
  "questions": [
    {{
      "id": "q1",
      "question": "string",
      "options": ["A", "B", "C", "D"],
      "correct_index": 0,
      "explanation": "string",
      "difficulty": "easy"
    }}
  ]
}}
Difficulty mix: {difficulty}
Use only easy, medium, or hard for difficulty.
Document title: {document_title}
Document:
{_clip(document_text)}
""".strip()

    @staticmethod
    def chat(document_title: str, document_text: str, history: list[ChatMessage], message: str) -> str:
        turns = "\n".join(f"{item.role}: {item.content}" for item in history[-8:])
        return f"""
You are NeuroLearn AI. Answer using only the uploaded document.
If the answer is not supported by the document, say what is missing and suggest a related supported topic.
Return only valid JSON with this exact shape:
{{
  "answer": "string",
  "cited_insights": ["string"]
}}
Document title: {document_title}
Recent conversation:
{turns or "No prior conversation."}
Student question:
{message}
Document:
{_clip(document_text)}
""".strip()

