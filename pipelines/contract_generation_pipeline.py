from pathlib import Path

from HSE_Project_DocGen.services.llm_engine import LLMEngine
from services.extractor.validator import validate_extraction

from services.docx.docx_parser import DocxParser
from services.docx.chunker import DocxChunker
from services.docx.entity_replacer import DocxEntityReplacer
from services.docx.renderer import DocxRenderer

from services.replacer.transform_utils import transform_big_chunks
from services.replacer.docx_parser import iter_all_runs, extract_run_texts
from docx import Document

from utils.logger import logger


class ContractGenerationPipeline:
    def __init__(self, model_path: str, template_path: str):
        self.office_clerk = LLMEngine(model_path)
        
    def run(self, prompt: str, extractor_system_prompt_path: str, replacer_system_prompt_path):
        logger.info("Pipeline started")
        logger.info(f"User prompt: {prompt}")
        
        # extraction
        logger.info("Running LLM extraction")
        raw_output = self.office_clerk.extract(prompt, extractor_system_prompt_path)
        logger.info(f"LLM raw output: {raw_output}")
        extracted = validate_extraction(raw_output)
        logger.info(f"Extraction validated, extracted structure: {extracted}")

        self.office_clerk.construct_replacement_prompt(replacer_system_prompt_path, format_extracted(extracted))
        
        doc = Document(src_path)
        original_texts = extract_run_texts(doc)

        new_texts = transform_big_chunks(original_texts, lambda x: self.office_clerk.replace_in_chunk(x))

        text_iter = iter(new_texts)
        for run in iter_all_runs(doc):
            run.text = next(text_iter)

        doc.save(dst_path)
        

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
