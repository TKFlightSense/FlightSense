from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ReviewIn(BaseModel):
    id: Optional[str] = None
    text: str
    route: Optional[str] = None
    cabin: Optional[str] = None
    date: Optional[str] = None  # ISO8601


class MultiLabelOut(BaseModel):
    review_id: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    scores: Dict[str, float] = Field(default_factory=dict)
