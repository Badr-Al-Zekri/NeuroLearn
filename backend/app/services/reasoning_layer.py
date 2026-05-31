from app.models.schemas import RetrievedChunk


class ReasoningPlan:
    def __init__(self, *, intent: str, strategy: str, constraints: list[str]) -> None:
        self.intent = intent
        self.strategy = strategy
        self.constraints = constraints

    def to_prompt_directive(self) -> str:
        constraints = "\n".join(f"- {item}" for item in self.constraints)
        return f"Intent: {self.intent}\nTutoring strategy: {self.strategy}\nConstraints:\n{constraints}"


class ReasoningLayer:
    def plan_grounded_tutor_response(self, *, message: str, chunks: list[RetrievedChunk]) -> ReasoningPlan:
        lowered = message.lower()
        if any(term in lowered for term in ["quiz", "test", "practice", "exam"]):
            intent = "assessment_preparation"
            strategy = "Use active recall, identify likely misconceptions, and provide one check-for-understanding question."
        elif any(term in lowered for term in ["explain", "what is", "define", "meaning"]):
            intent = "concept_explanation"
            strategy = "Explain from the source context first, then give a compact university-level example."
        else:
            intent = "study_support"
            strategy = "Answer directly, connect the response to key concepts, and suggest the next useful study step."

        chunk_refs = [chunk.metadata.heading or f"chunk {chunk.metadata.chunk_index + 1}" for chunk in chunks[:4]]
        constraints = [
            "Use only the retrieved context as factual grounding.",
            "Say when the retrieved context is insufficient.",
            "Prefer educational clarity over broad generality.",
            f"Relevant context references: {', '.join(chunk_refs) if chunk_refs else 'none'}",
        ]
        return ReasoningPlan(intent=intent, strategy=strategy, constraints=constraints)


reasoning_layer = ReasoningLayer()

