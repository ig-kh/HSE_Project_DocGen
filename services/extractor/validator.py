import json
from schemas.extraction import ExtractedContract

import re
import json
from typing import Literal, Optional, List
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator


Currency = Literal["RUB", "USD", "EUR", "GBP", "UNKNOWN"]
Vat = Literal["included", "excluded", "unknown"]
MissingField = Literal["date", "counterparty", "work", "work_time_days", "cost"]

DATE_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")
AMOUNT_RE = re.compile(r"^\d+(\.\d+)?$")


class Cost(BaseModel):
    amount: str = Field(default="", description="Digits with optional '.' decimal separator, no spaces")
    currency: Currency = "UNKNOWN"
    vat: Vat = "unknown"

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: str) -> str:
        if v is None:
            return ""
        v = v.strip()
        if v == "":
            return ""
        if not AMOUNT_RE.fullmatch(v):
            raise ValueError("cost.amount must be digits with optional decimal dot (e.g. '1000000' or '1999.99')")
        return v


class ParsedContract(BaseModel):
    date: Optional[str] = Field(default=None, description="dd.mm.yy")
    city: Optional[str] = None
    counterparty: Optional[str] = None
    work: Optional[str] = None

    work_time_days: Optional[int] = Field(default=None, ge=1, le=36500)
    work_time_basis_event: Optional[str] = Field(default=None)

    cost: Cost = Field(default_factory=Cost)
    missing_fields: List[MissingField] = Field(default_factory=list)

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not DATE_RE.fullmatch(v):
            raise ValueError("date must be in dd.mm.yyyy format (e.g. '21.04.2026')")
        return v

    @field_validator("city", "counterparty", "work", "work_time_basis_event")
    @classmethod
    def strip_or_none(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        return v if v else None

    @model_validator(mode="after")
    def apply_defaults_and_cleanup(self) -> "ParsedContract":
        # Default basis event
        if self.work_time_basis_event is None:
            self.work_time_basis_event = "contract_date"

        # Deduplicate missing_fields preserving order
        seen = set()
        deduped = []
        for f in self.missing_fields:
            if f not in seen:
                seen.add(f)
                deduped.append(f)
        self.missing_fields = deduped

        return self
    
def validate_extraction(text: str) -> ParsedContract:
    data = json.loads(text)
    return ParsedContract.model_validate(data)

# def validate_extraction(raw_output: str) -> ExtractedContract:
#     data = json.loads(raw_output)
#     return ExtractedContract(**data)