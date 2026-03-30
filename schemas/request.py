from pydantic import BaseModel


class GenerateContractRequest(BaseModel):
    prompt: str
