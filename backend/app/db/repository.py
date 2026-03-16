from sqlalchemy.orm import Session

from app.db.models import Template, GeneratedContract


class TemplateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_type(self, contract_type: str):
        return (
            self.db.query(Template)
            .filter(Template.contract_type == contract_type)
            .first()
        )


class ContractRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_generated_contract(
        self,
        prompt,
        extracted_json,
        template_id,
        file_path
    ):
        contract = GeneratedContract(
            prompt=prompt,
            extracted_json=extracted_json,
            template_id=template_id,
            file_path=file_path
        )
        self.db.add(contract)
        self.db.commit()
        return contract
