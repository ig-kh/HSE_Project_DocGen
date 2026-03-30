from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from api.config import settings
from schemas.request import GenerateContractRequest
from api.dependencies import get_pipeline
from pipelines.contract_generation_pipeline import ContractGenerationPipeline

router = APIRouter()


@router.post("/generate")
async def generate_contract(
    req: GenerateContractRequest,
    pipeline: ContractGenerationPipeline = Depends(get_pipeline),
):
    result = pipeline.run(
        req.prompt,
        settings.EXTRACTOR_SYSTEM_PROMPT_PATH,
        settings.REPLACER_SYSTEM_PROMPT_PATH,
    )

    output_path = Path(result["contract_path"])
    if not output_path.exists():
        raise HTTPException(status_code=500, detail="Processed document was not created")

    return FileResponse(
        path=output_path,
        media_type=(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        filename=output_path.name,
    )
