from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class DebateBase(BaseModel):
    """Schema for debates."""
    title: str
    description: str
    policy_text: Optional[str] = None

class DebateCreate(DebateBase):
    """Schema for creating a new debate."""
    pass

class DebateResponse(DebateBase):
    """Schema for debate responses."""
    id: int
    status: str
    created_at: datetime
    paper_id: Optional[int] = None

    class Config:
        from_attributes = True

class MPResponseBase(BaseModel):
    """Schema for MP responses in debates."""
    mp_role: str
    content: str
    color: Optional[str] = "#000000"

class MPResponse(MPResponseBase):
    """Schema for MP responses in debates."""
    id: int
    debate_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class VoteBase(BaseModel):
    """Schema for votes."""
    mp_role: str
    vote: str
    reasoning: str

class Vote(VoteBase):
    """Schema for votes."""
    id: int
    debate_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class VoteResponse(VoteBase):
    """Schema for votes."""
    id: int
    debate_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class VoteSummary(BaseModel):
    """Schema for vote summaries."""
    for_votes: int
    against_votes: int
    abstain_votes: int
    total_votes: int
    result: str

class VoteMetricsSummary(BaseModel):
    average_consistency: float
    total_votes: int
    low_consistency_count: int
    time_window: str

class RoleMetrics(BaseModel):
    average_consistency: float
    total_votes: int
    low_consistency_votes: int

class VoteDistribution(BaseModel):
    for_votes: int
    against_votes: int
    abstain_votes: int

class DebateMetrics(BaseModel):
    debate_id: int
    average_consistency: float
    votes_by_role: Dict[str, int]
    vote_decisions: VoteDistribution
    metrics: Optional[Dict[str, float]] = None
    message: Optional[str] = None
