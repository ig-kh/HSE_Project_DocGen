from pathlib import Path

from services.extractor.llm_extractor import LLMExtractor
from services.extractor.validator import validate_extraction

from services.docx.docx_parser import DocxParser
from services.docx.chunker import DocxChunker
from services.docx.entity_replacer import DocxEntityReplacer
from services.docx.renderer import DocxRenderer

from utils.exceptions import (
    ExtractionError,
    ValidationError,
    DocxProcessingError,
    PipelineError
)

from utils.logger import logger


class ContractGenerationPipeline:
    def __init__(self, model_path: str, template_path: str):
        self.extractor = LLMExtractor(model_path)
        self.chunker = DocxChunker()
        self.entity_replacer = DocxEntityReplacer(self.extractor)
        self.renderer = DocxRenderer()
        self.template_path = template_path
        
    def run(self, prompt: str, system_prompt_path: str):
        logger.info("Pipeline started")
        logger.info(f"User prompt: {prompt}")
        
        # extraction
        logger.info("Running LLM extraction")
        raw_output = self.extractor.extract(prompt, system_prompt_path)
        logger.info(f"LLM raw output: {raw_output}")
        extracted = validate_extraction(raw_output)
        logger.info("Extraction validated")

        # load docx
        logger.info("Loading template")
        parser = DocxParser(self.template_path)
        paragraphs_xml = parser.get_paragraphs()
        paragraphs_text = [
            parser.get_paragraph_text(p) for p in paragraphs_xml
        ]
        logger.info(f"Document paragraphs: {len(paragraphs_text)}")

        # chunking
        chunks = self.chunker.chunk(paragraphs_text)
        logger.info(f"Chunks created: {len(chunks)}")

        # entity replacement
        logger.info("Running entity replacement")
        self.entity_replacer.process_chunks(chunks, parser)

        # rendering
        logger.info("Rendering placeholders")
        self.renderer.render(parser, extracted)

        # save document
        output_path = self._generate_output_path()
        parser.save(output_path)
        logger.info(f"Contract saved: {output_path}")

        return {
            "extracted": extracted,
            "contract_path": str(output_path)
        }

    def _generate_output_path(self):
        output_dir = Path("generated_contracts")
        output_dir.mkdir(exist_ok=True)
        filename = f"contract_{self._random_id()}.docx"
        return output_dir / filename

    def _random_id(self):
        import uuid
        return uuid.uuid4().hex[:8]
