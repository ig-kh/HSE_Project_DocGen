from typing import List
from app.services.docx.chunker import DocxChunk
from app.services.docx.entity_cache import EntityCache


class DocxEntityReplacer:
    """
    Replaces entities inside DOCX XML paragraphs using LLM-based NER.
    """

    def __init__(self, llm_extractor):

        self.llm = llm_extractor
        self.cache = EntityCache()

    def process_chunks(self, chunks: List[DocxChunk], parser):
        """
        Process all chunks and update DOCX XML.
        """

        for chunk in chunks:

            replaced_text = self.llm_replace_entities(chunk.text)

            self.apply_replacement(parser, chunk, replaced_text)

    def llm_replace_entities(self, text: str) -> str:
        cached = self.cache.get(text)
        if cached:
            return cached
        
        prompt = f"""Replace entities in the legal document text with placeholders.
        Text: {text}"""
        
        response = self.llm.extract(prompt)
        result = response.strip()
        self.cache.set(text, result)
        
        return result

    def apply_replacement(self, parser, chunk: DocxChunk, replaced_text: str):
        """
        Replace text in XML paragraphs.
        """

        paragraphs = parser.get_paragraphs()

        new_parts = replaced_text.split("\n")

        for idx, paragraph_idx in enumerate(chunk.paragraph_indices):

            if idx >= len(new_parts):
                break

            paragraph = paragraphs[paragraph_idx]

            self.update_paragraph_text(parser, paragraph, new_parts[idx])

    def update_paragraph_text(self, parser, paragraph, new_text: str):
        """
        Replace text inside <w:t> nodes of paragraph.
        """

        texts = paragraph.xpath(".//w:t", namespaces=parser.ns)

        if not texts:
            return

        texts[0].text = new_text

        for t in texts[1:]:
            t.text = ""