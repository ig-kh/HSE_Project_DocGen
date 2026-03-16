from fastapi import APIRouter, Depends

from app.schemas.request import GenerateContractRequest
from app.api.dependencies import get_pipeline
from app.pipelines.contract_generation_pipeline import ContractGenerationPipeline


router = APIRouter()

@router.post("/generate")
async def generate_contract(
    req: GenerateContractRequest,
    pipeline: ContractGenerationPipeline = Depends(get_pipeline)
):
    result = pipeline.run(req.prompt)

    return result