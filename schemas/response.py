from pydantic import BaseModel
from schemas.extraction import ExtractedContract


class GenerateContractResponse(BaseModel):
    extracted: ExtractedContract
    contract_path: str
