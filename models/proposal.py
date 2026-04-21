from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Proposal(BaseModel):
    id: Optional[str] = None
    lead_id: Optional[str] = None
    prospect_name: str
    prospect_company: str
    pricing_tier: str
    pain_points: List[str]
    proposed_solution: Optional[str] = None
    content: str = ""
    price: Optional[str] = None
    status: str = "draft"
    created_at: datetime = datetime.now()
    sent_at: Optional[datetime] = None
