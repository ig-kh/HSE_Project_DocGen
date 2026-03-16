from pydantic import BaseModel
from app.schemas.extraction import ExtractedContract


class GenerateContractResponse(BaseModel):
    extracted: ExtractedContract
    contract_path: str