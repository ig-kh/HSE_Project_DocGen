from fastapi import APIRouter, Depends

from schemas.request import GenerateContractRequest
from api.dependencies import get_pipeline
from pipelines.contract_generation_pipeline import ContractGenerationPipeline

SYSTEM_PROMPT_PATH = 'services/extractor/system_prompt.txt'

router = APIRouter()

@router.post("/generate")
async def generate_contract(
    req: GenerateContractRequest,
    pipeline: ContractGenerationPipeline = Depends(get_pipeline)
):
    result = pipeline.run(req.prompt, SYSTEM_PROMPT_PATH)

    return result