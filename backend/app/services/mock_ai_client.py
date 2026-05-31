from app.models.schemas import ChatMessage, ChatResponse, QuizQuestion, QuizResponse, SummaryResponse


class MockAIClient:
    async def summarize(self, *, title: str, content: str, tone: str) -> SummaryResponse:
        words = content.split()
        focus = " ".join(words[:18]) if words else title
        return SummaryResponse(
            title=f"{title} study brief",
            overview=f"This material introduces the core ideas around {focus}. It has enough structure for a focused review session and can be converted into practice questions.",
            key_insights=[
                "The document contains several learnable concepts that can be grouped into definitions, relationships, and applications.",
                "The strongest study path is to identify the main claims, then connect each claim to examples from the source.",
                "A short active-recall loop will work better than rereading because the content has clear question-and-answer potential.",
            ],
            study_actions=[
                "Review the overview, then rewrite it in your own words without looking.",
                "Answer the generated quiz and revisit explanations for missed questions.",
                "Use the chat panel to ask for examples, analogies, and likely exam angles.",
            ],
            confidence=0.86,
            source_coverage="Mock mode analyzed the extracted text shape and produced deterministic demo-ready guidance.",
        )

    async def generate_quiz(self, *, title: str, content: str, question_count: int, difficulty: str) -> QuizResponse:
        questions = [
            QuizQuestion(
                id=f"q{i + 1}",
                question=f"Which study action best helps retain the key ideas in {title}?",
                options=[
                    "Passively reread the full document several times",
                    "Use active recall and explain concepts from memory",
                    "Skip the examples and memorize only headings",
                    "Focus only on formatting and layout",
                ],
                correct_index=1,
                explanation="Active recall strengthens retrieval and exposes weak understanding more clearly than rereading.",
                difficulty=["easy", "medium", "hard"][i % 3],
            )
            for i in range(question_count)
        ]
        return QuizResponse(title=f"{title} practice quiz", questions=questions)

    async def chat(self, *, title: str, content: str, history: list[ChatMessage], message: str) -> ChatResponse:
        return ChatResponse(
            answer=f"Based on the uploaded material for {title}, a useful way to approach this is to connect your question, \"{message}\", back to the document's main concepts, then test yourself with one concrete example.",
            cited_insights=[
                "The uploaded content is available in the current learning session.",
                "Use the summary and quiz together for a stronger review loop.",
            ],
        )

