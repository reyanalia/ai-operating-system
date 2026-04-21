from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class Report(BaseModel):
    id: Optional[str] = None
    report_type: str
    metrics: List[str]
    data: Dict[str, Any] = {}
    content: str = ""
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    format: str = "summary"
    created_at: datetime = datetime.now()
    recipients: List[str] = []
    sent: bool = False
