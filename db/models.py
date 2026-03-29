from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime

from db.session import Base


class Template(Base):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contract_type = Column(String, index=True)
    file_path = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class GeneratedContract(Base):
    __tablename__ = "generated_contracts"
    id = Column(Integer, primary_key=True)
    prompt = Column(String)
    extracted_json = Column(JSON)
    template_id = Column(Integer)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)