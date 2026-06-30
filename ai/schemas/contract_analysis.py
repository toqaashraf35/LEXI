from pydantic import BaseModel
from typing import List, Optional


class ClauseResult(BaseModel):
    clause_id: int
    clause_text: str
    risk: str
    risk_type: Optional[str]
    risk_parties: List[str]
    explanation: Optional[str]
    risk_level: Optional[str]
    recommendation: Optional[str]


class ContractAnalysisResponse(BaseModel):
    contract_analysis: List[ClauseResult]
    summary: dict


class AnalyzeRequest(BaseModel):
    file_path: str
    contract_type: str = "عام"
    contract_subtype: str = "عام"