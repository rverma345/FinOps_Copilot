from typing import List,Optional,dict,Any,Dict
from pydantic import BaseModel

class KPIResponse(BaseModel):
    kpi_name=str
    data: List[Dict[str,Any]]

class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: List[str]
    suggestions: list[str]
    table: Optional[list[Dict[str,Any]]]= None
    chart: Optional[str] = None


    