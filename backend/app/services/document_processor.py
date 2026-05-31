import re
from hashlib import sha256
from app.core.config import get_settings
from app.models.schemas import (
    ChunkMetadata,
    DocumentChunk,
    DocumentKind,
    KnowledgeRelationship,
    LearningObjective,
    LearningConcept,
    LearningTopic,
    ProcessedDocument,
    RelationshipType,
)


class DocumentProcessingPipeline:
    def __init__(self) -> None:
        self._settings = get_settings()

    def process(self, *, document_id: str, title: str, kind: DocumentKind, raw_text: str) -> ProcessedDocument:
        cleaned = self._clean(raw_text)
        normalized = self._normalize(cleaned)
        concepts = self._extract_concepts(normalized)
        topics = self._extract_topics(concepts, normalized)
        objectives = self._build_learning_objectives(document_id, concepts)
        relationships = self._build_relationships(concepts, objectives)
        chunks = self._semantic_chunks(
            document_id=document_id,
            title=title,
            kind=kind,
            text=normalized,
            concepts=concepts,
            objectives=objectives,
        )
        return ProcessedDocument(
            document_id=document_id,
            title=title,
            kind=kind,
            normalized_text=normalized,
            chunks=chunks,
            concepts=concepts,
            topics=topics,
            learning_objectives=objectives,
            relationships=relationships,
        )

    def _clean(self, text: str) -> str:
        text = text.replace("\x00", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"(?m)^\s*\d+\s*$", "", text)
        return text.strip()

    def _normalize(self, text: str) -> str:
        paragraphs = [line.strip() for line in text.splitlines()]
        paragraphs = [line for line in paragraphs if line]
        return "\n\n".join(paragraphs)

    def _semantic_chunks(
        self,
        *,
        document_id: str,
        title: str,
        kind: DocumentKind,
        text: str,
        concepts: list[LearningConcept],
        objectives: list[LearningObjective],
    ) -> list[DocumentChunk]:
        units = self._semantic_units(text)
        target_words = self._settings.chunk_target_tokens
        overlap_words = self._settings.chunk_overlap_tokens
        chunks: list[DocumentChunk] = []
        buffer: list[SemanticUnit] = []
        buffer_words = 0
        index = 0

        for unit in units:
            if buffer and (unit.is_heading or buffer_words + unit.word_count > target_words):
                chunks.append(self._build_chunk(document_id, title, kind, index, buffer, concepts, objectives))
                index += 1
                overlap = self._overlap_unit(buffer, overlap_words)
                buffer = [overlap] if overlap else []
                buffer_words = overlap.word_count if overlap else 0
            buffer.append(unit)
            buffer_words += unit.word_count

        if buffer:
            chunks.append(self._build_chunk(document_id, title, kind, index, buffer, concepts, objectives))
        return chunks

    def _semantic_units(self, text: str) -> list["SemanticUnit"]:
        raw_units = [item.strip() for item in re.split(r"\n\s*\n", text) if item.strip()]
        units: list[SemanticUnit] = []
        section_path: list[str] = []
        for unit in raw_units:
            is_heading = self._is_heading(unit)
            if is_heading:
                section_path = self._updated_section_path(section_path, unit)
            words = unit.split()
            if len(words) <= self._settings.chunk_target_tokens:
                units.append(SemanticUnit(text=unit, section_path=section_path.copy(), is_heading=is_heading))
                continue
            for start in range(0, len(words), self._settings.chunk_target_tokens):
                units.append(
                    SemanticUnit(
                        text=" ".join(words[start : start + self._settings.chunk_target_tokens]),
                        section_path=section_path.copy(),
                        is_heading=False,
                    )
                )
        return units

    def _overlap_unit(self, buffer: list["SemanticUnit"], overlap_words: int) -> "SemanticUnit | None":
        if not buffer:
            return None
        section_path = buffer[-1].section_path
        overlap = " ".join(" ".join(unit.text for unit in buffer).split()[-overlap_words:])
        if not overlap:
            return None
        return SemanticUnit(text=overlap, section_path=section_path, is_heading=False)

    def _build_chunk(
        self,
        document_id: str,
        title: str,
        kind: DocumentKind,
        index: int,
        units: list["SemanticUnit"],
        concepts: list[LearningConcept],
        objectives: list[LearningObjective],
    ) -> DocumentChunk:
        text = "\n\n".join(unit.text for unit in units).strip()
        chunk_concepts = [concept.name for concept in concepts if concept.name.lower() in text.lower()][:8]
        section_path = units[-1].section_path if units else []
        heading = section_path[-1] if section_path else self._detect_heading(units[0].text)
        objective_ids = [
            objective.objective_id
            for objective in objectives
            if set(objective.concept_ids).intersection({concept.concept_id for concept in concepts if concept.name in chunk_concepts})
        ][:4]
        metadata = ChunkMetadata(
            document_id=document_id,
            title=title,
            chunk_index=index,
            heading=heading,
            section_path=section_path,
            source_kind=kind,
            word_count=len(text.split()),
            token_estimate=max(1, int(len(text.split()) * 1.3)),
            topics=self._topic_hints(text),
            concepts=chunk_concepts,
            learning_objective_ids=objective_ids,
            difficulty=self._estimate_difficulty(text),
            metadata={"chunking_strategy": "heading_paragraph_token_window"},
        )
        chunk_hash = sha256(f"{document_id}:{index}:{text[:80]}".encode("utf-8")).hexdigest()[:16]
        return DocumentChunk(chunk_id=f"{document_id}:{chunk_hash}", text=text, metadata=metadata)

    def _detect_heading(self, text: str) -> str | None:
        first_line = text.splitlines()[0].strip()
        if self._is_heading(first_line):
            return first_line
        return None

    def _is_heading(self, text: str) -> bool:
        candidate = text.strip()
        words = candidate.split()
        if not candidate or len(words) > 12 or len(candidate) > 96:
            return False
        if re.match(r"^(\d+(\.\d+)*|chapter|unit|module|section)\b", candidate, flags=re.IGNORECASE):
            return True
        letters = [char for char in candidate if char.isalpha()]
        if letters and sum(1 for char in letters if char.isupper()) / len(letters) > 0.65:
            return True
        return len(words) <= 7 and candidate.endswith(":")

    def _updated_section_path(self, current: list[str], heading: str) -> list[str]:
        level = heading.count(".") + 1 if re.match(r"^\d+(\.\d+)*\b", heading) else 1
        return [*current[: max(0, level - 1)], heading.rstrip(":")]

    def _topic_hints(self, text: str) -> list[str]:
        words = [word.lower() for word in re.findall(r"[A-Za-z][A-Za-z\-]{4,}", text)]
        stop = {"their", "there", "which", "about", "these", "those", "where", "while", "because", "through"}
        counts: dict[str, int] = {}
        for word in words:
            if word not in stop:
                counts[word] = counts.get(word, 0) + 1
        return [word for word, _ in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:5]]

    def _extract_concepts(self, text: str) -> list[LearningConcept]:
        names = self._topic_hints(text)[:12]
        concepts: list[LearningConcept] = []
        for name in names:
            concept_id = sha256(name.encode("utf-8")).hexdigest()[:12]
            concepts.append(
                LearningConcept(
                    concept_id=concept_id,
                    name=name.title(),
                    description=f"Core learning concept inferred from repeated source language around {name}.",
                    difficulty="intermediate" if len(name) > 9 else "introductory",
                )
            )
        return concepts

    def _extract_topics(self, concepts: list[LearningConcept], text: str) -> list[LearningTopic]:
        if not concepts:
            return []
        topic_names = [concept.name for concept in concepts[:4]]
        topic_id = sha256("|".join(topic_names).encode("utf-8")).hexdigest()[:12]
        return [
            LearningTopic(
                topic_id=topic_id,
                name=", ".join(topic_names[:2]),
                summary=f"Primary topic cluster covering {', '.join(topic_names)}.",
                concept_ids=[concept.concept_id for concept in concepts[:6]],
            )
        ]

    def _build_learning_objectives(self, document_id: str, concepts: list[LearningConcept]) -> list[LearningObjective]:
        objectives: list[LearningObjective] = []
        for concept in concepts[:8]:
            objective_id = sha256(f"{document_id}:{concept.concept_id}:objective".encode("utf-8")).hexdigest()[:12]
            objectives.append(
                LearningObjective(
                    objective_id=objective_id,
                    document_id=document_id,
                    description=f"Explain and apply the concept of {concept.name} using evidence from the learning material.",
                    concept_ids=[concept.concept_id],
                    bloom_level="apply" if getattr(concept.difficulty, "value", concept.difficulty) == "intermediate" else "understand",
                    difficulty=concept.difficulty,
                )
            )
        return objectives

    def _build_relationships(
        self,
        concepts: list[LearningConcept],
        objectives: list[LearningObjective],
    ) -> list[KnowledgeRelationship]:
        relationships: list[KnowledgeRelationship] = []
        for previous, current in zip(concepts, concepts[1:], strict=False):
            relationship_id = sha256(f"{previous.concept_id}:{current.concept_id}:supports".encode("utf-8")).hexdigest()[:12]
            relationships.append(
                KnowledgeRelationship(
                    relationship_id=relationship_id,
                    source_id=previous.concept_id,
                    target_id=current.concept_id,
                    relationship_type=RelationshipType.supports,
                    strength=0.42,
                    rationale="Concepts appear together in the source material and should be reviewed as a cluster.",
                )
            )
        for objective in objectives:
            for concept_id in objective.concept_ids:
                relationship_id = sha256(f"{concept_id}:{objective.objective_id}:assessed_by".encode("utf-8")).hexdigest()[:12]
                relationships.append(
                    KnowledgeRelationship(
                        relationship_id=relationship_id,
                        source_id=concept_id,
                        target_id=objective.objective_id,
                        relationship_type=RelationshipType.assessed_by,
                        strength=0.7,
                        rationale="The learning objective measures understanding of this concept.",
                    )
                )
        return relationships

    def _estimate_difficulty(self, text: str) -> str:
        words = text.split()
        if not words:
            return "introductory"
        average_word_length = sum(len(word) for word in words) / len(words)
        long_word_ratio = len([word for word in words if len(word) > 10]) / len(words)
        if average_word_length > 6.4 or long_word_ratio > 0.16:
            return "advanced"
        if average_word_length > 5.4 or long_word_ratio > 0.08:
            return "intermediate"
        return "introductory"


class SemanticUnit:
    def __init__(self, *, text: str, section_path: list[str], is_heading: bool) -> None:
        self.text = text
        self.section_path = section_path
        self.is_heading = is_heading
        self.word_count = len(text.split())


document_processor = DocumentProcessingPipeline()
