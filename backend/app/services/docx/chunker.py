from typing import List
from dataclasses import dataclass


@dataclass
class DocxChunk:
    """
    Represents a chunk of text extracted from docx paragraphs
    """
    chunk_id: int
    paragraph_indices: List[int]
    text: str


class DocxChunker:
    """
    Splits DOCX paragraphs into chunks suitable for LLM processing.
    """

    def __init__(self, max_chars: int = 1200):
        """
        max_chars — maximum size of chunk text
        """
        self.max_chars = max_chars

    def chunk(self, paragraphs: List[str]) -> List[DocxChunk]:
        """
        Convert paragraphs into LLM-friendly chunks.
        """
        chunks: List[DocxChunk] = []

        current_paragraphs = []
        current_indices = []
        current_length = 0
        chunk_id = 0
        for idx, paragraph in enumerate(paragraphs):
            paragraph_length = len(paragraph)
            if paragraph_length > self.max_chars:
                if current_paragraphs:
                    chunks.append(
                        DocxChunk(
                            chunk_id=chunk_id,
                            paragraph_indices=current_indices,
                            text="\n".join(current_paragraphs),
                        )
                    )
                    chunk_id += 1
                    current_paragraphs = []
                    current_indices = []
                    current_length = 0

                chunks.append(
                    DocxChunk(
                        chunk_id=chunk_id,
                        paragraph_indices=[idx],
                        text=paragraph,
                    )
                )
                chunk_id += 1
                continue

            if current_length + paragraph_length > self.max_chars:
                chunks.append(
                    DocxChunk(
                        chunk_id=chunk_id,
                        paragraph_indices=current_indices,
                        text="\n".join(current_paragraphs),
                    )
                )
                chunk_id += 1
                current_paragraphs = []
                current_indices = []
                current_length = 0

            current_paragraphs.append(paragraph)
            current_indices.append(idx)
            current_length += paragraph_length

        if current_paragraphs:
            chunks.append(
                DocxChunk(
                    chunk_id=chunk_id,
                    paragraph_indices=current_indices,
                    text="\n".join(current_paragraphs),
                )
            )

        return chunks
