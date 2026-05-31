from app.models.schemas import DocumentKind
from app.services.document_processor import document_processor


def test_processor_preserves_heading_boundaries_and_learning_metadata():
    text = """
1 Foundations of Memory

Active recall helps learners strengthen memory because retrieval practice forces the brain to reconstruct knowledge.

Spaced repetition improves long term retention by revisiting concepts after increasing intervals.

2 Feedback Loops

Feedback helps students correct mistakes and focus future study sessions on the concepts that still feel uncertain.
"""

    processed = document_processor.process(document_id="doc-processor", title="Learning science", kind=DocumentKind.text, raw_text=text)

    assert processed.chunks
    assert processed.concepts
    assert processed.learning_objectives
    assert processed.relationships
    assert any(chunk.metadata.section_path for chunk in processed.chunks)
    assert all(chunk.metadata.metadata["chunking_strategy"] == "heading_paragraph_token_window" for chunk in processed.chunks)
