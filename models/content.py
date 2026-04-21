from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ContentPiece(BaseModel):
    id: Optional[str] = None
    source_type: str
    source_content: str
    channel: str
    repurposed_content: str = ""
    platform_format: Optional[str] = None
    char_count: Optional[int] = None
    status: str = "draft"
    scheduled_at: Optional[datetime] = None
    created_at: datetime = datetime.now()
