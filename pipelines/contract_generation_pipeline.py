from pathlib import Path

from api.config import settings
from services.llm_engine import LLMEngine
from services.extractor.validator import validate_extraction

from services.replacer.transform_utils import transform_big_chunks
from services.replacer.docx_parser import iter_all_runs, extract_run_texts
from docx import Document

from docx.enum.text import WD_COLOR

from utils.logger import logger

def process(x, model):
    logger.info(">" + x.replace("➡️", ""))
    y = model.replace_in_chunk(x)
    logger.info("<" + y.replace("➡️", ""))
    return y


class ContractGenerationPipeline:
    def __init__(self, model_path: str | Path, template_path: str | Path):
        self.office_clerk = LLMEngine(model_path)
        self.template_path = template_path

    def run(
        self,
        prompt: str,
        extractor_system_prompt_path: str | Path,
        replacer_system_prompt_path: str | Path,
    ):
        logger.info("Pipeline started")
        logger.info(f"User prompt: {prompt}")

        # extraction
        logger.info("Running LLM extraction")
        raw_output = self.office_clerk.extract(prompt, extractor_system_prompt_path)
        logger.info(f"LLM raw output: {raw_output}")
        extracted = validate_extraction(raw_output)  # dict with correct fields
        logger.info(f"Extraction validated, extracted structure: {extracted}")

        self.office_clerk.construct_replacement_prompt(
            replacer_system_prompt_path, extracted
        )
        logger.info("Generated prompt for replacer:")
        logger.info(self.office_clerk.replacement_prompt)

        doc = Document(settings.RAW_DOC_PATH)
        original_texts = extract_run_texts(doc)

        new_texts = transform_big_chunks(
            original_texts, lambda x: process(x, self.office_clerk)
        )

        text_iter = iter(new_texts)
        for run, old_run_text in zip(iter_all_runs(doc), original_texts):
            new_run_text = next(text_iter)
            run.text = new_run_text
            if settings.ENABLE_DIFF_HIGHLIGHTING and (old_run_text != new_run_text):
                run.font.highlight_color = WD_COLOR.TURQUOISE

        output_path = settings.PROCESSED_DOC_PATH
        doc.save(output_path)

        return {"extracted": extracted, "contract_path": str(output_path)}

    def _generate_output_path(self):
        output_dir = settings.GENERATED_CONTRACTS_DIR
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"contract_{self._random_id()}.docx"
        return output_dir / filename

    def _random_id(self):
        import uuid

        return uuid.uuid4().hex[:8]
