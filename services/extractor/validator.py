import json
from schemas.extraction import ExtractedContract

def validate_extraction(raw_output: str) -> ExtractedContract:
    data = json.loads(raw_output)
    return ExtractedContract(**data)
