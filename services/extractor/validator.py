import json
from schemas.extraction import ExtractedContract
import moneytalks as mt

import re
import json
from typing import Literal, Optional, List
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator


Currency = Literal["RUB", "USD", "EUR", "GBP", "UNKNOWN"]
currency_replace_dict = {
    "USD": {
        'рубль': 'доллар',
        'рублей': 'долларов',
        'рубля': 'доллара',
        'копейка': 'цент',
        'копеек': 'центов',
        'копейки': 'цента'
    },
    "EUR": {
        'рубль': 'евро',
        'рублей': 'евро',
        'рубля': 'евро',
        'копейка': 'цент',
        'копеек': 'центов',
        'копейки': 'цента'
    },
    "GBP": {
        'рубль': 'фунт стерлингов',
        'рублей': 'фунтов стерлингов',
        'рубля': 'фунта стерлингов',
        'копейка': 'цент',
        'копеек': 'центов',
        'копейки': 'цента'
    },
}
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

def format_money(value: float) -> str:
    s = f"{value:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", " ")
    
    return s

def remove_invalid_thousand_phrase(text: str) -> str:
    pattern = r'\b(миллион|миллиона|миллионов)\s+тысяч\b'
    return re.sub(pattern, r'\1', text, flags=re.IGNORECASE)

def fix_currency(currency: str, text: str):
    if currency != "RUB":
        for pattern in ['рубль', 'рублей', 'рубля', 'копейка', 'копеек', 'копейки']:
            text = text.replace(pattern, currency_replace_dict[currency][pattern])
    return text
    
def format_extracted(extracted: ParsedContract) -> dict:
    cost_amount = float(extracted.cost.amount.replace(" ", "").replace(",", "."))
    cost_currency = extracted.cost.currency if extracted.cost.currency != "UNKNOWN" else "RUB"
    cost_vat = extracted.cost.vat
    print(cost_vat)
    vat_cost_str = ""
    if cost_vat == "included" or cost_vat == "unknown":
        vat_perc = 22
        vat_amount = cost_amount * (vat_perc / 100)
        vat_cost_str = f", в том числе НДС {vat_perc}% {format_money(vat_amount)} ({mt.get_string_by_number(vat_amount)})"
        
    full_cost_str = remove_invalid_thousand_phrase(f"{format_money(cost_amount)} ({mt.get_string_by_number(cost_amount)}){vat_cost_str}")
    full_cost_str = fix_currency(cost_currency, full_cost_str)
    
    formatted = {
        "data": extracted.date,
        "city": extracted.city if extracted.city is not None else "Nizhny Novgorod",
        "counterparty": extracted.counterparty,
        "work": extracted.work,
        "work_time_days": extracted.work_time_days,
        "work_time_basis_event": extracted.work_time_basis_event if extracted.work_time_basis_event is not None else "contract_date",
        "cost": full_cost_str
    }
    
    return formatted
    
def validate_extraction(text: str) -> ParsedContract:
    data = json.loads(text)
    return format_extracted(ParsedContract.model_validate(data))