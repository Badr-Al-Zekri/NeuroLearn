from app.models.schemas import RetrievedChunk


class ContextBuilder:
    def build(self, chunks: list[RetrievedChunk], max_words: int = 1800) -> str:
        parts: list[str] = []
        used_words = 0
        for chunk in chunks:
            words = chunk.text.split()
            remaining = max_words - used_words
            if remaining <= 0:
                break
            clipped = " ".join(words[:remaining])
            heading = chunk.metadata.heading or f"Chunk {chunk.metadata.chunk_index + 1}"
            parts.append(f"[{heading} | score={chunk.score:.3f}]\n{clipped}")
            used_words += len(clipped.split())
        return "\n\n".join(parts)


context_builder = ContextBuilder()

