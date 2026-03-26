from fastapi import APIRouter, Depends

from schemas.request import GenerateContractRequest
from api.dependencies import get_pipeline
from pipelines.contract_generation_pipeline import ContractGenerationPipeline

EXTRACTOR_SYSTEM_PROMPT_PATH = 'services/extractor/system_prompt.txt'
REPLACER_SYSTEM_PROMPT_PATH = 'services/replacer/sys_prompt_template.txt'

router = APIRouter()

@router.post("/generate")
async def generate_contract(
    req: GenerateContractRequest,
    pipeline: ContractGenerationPipeline = Depends(get_pipeline)
):
    result = pipeline.run(req.prompt, EXTRACTOR_SYSTEM_PROMPT_PATH, REPLACER_SYSTEM_PROMPT_PATH)

    return result