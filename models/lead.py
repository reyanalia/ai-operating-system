from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class LeadStatus(str, Enum):
    NEW = "new"
    QUALIFIED = "qualified"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATING = "negotiating"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class Lead(BaseModel):
    id: Optional[str] = None
    name: str
    company: str
    email: str
    phone: Optional[str] = None
    company_size: Optional[str] = None
    status: LeadStatus = LeadStatus.NEW
    pain_points: List[str] = []
    source: Optional[str] = None
    score: Optional[int] = None
    score_grade: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = datetime.now()
    last_updated: Optional[datetime] = None
