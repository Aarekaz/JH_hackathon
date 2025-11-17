from datetime import datetime
from typing import Dict, List, Optional, Literal

from pydantic import BaseModel, Field, field_validator, ConfigDict


class DebateBase(BaseModel):
    """Schema for debates with validation."""
    title: str = Field(..., min_length=10, max_length=500, description="Debate title (10-500 characters)")
    description: str = Field(..., min_length=20, max_length=2000, description="Debate description (20-2000 characters)")
    policy_text: Optional[str] = Field(None, max_length=10000, description="Policy text (max 10000 characters)")

    @field_validator('title', 'description')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure title and description are not just whitespace."""
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or only whitespace')
        return v.strip()

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
    """Schema for MP responses in debates with validation."""
    mp_role: Literal["corporate", "academic", "government", "civil_rights"] = Field(
        ...,
        description="MP role (must be one of: corporate, academic, government, civil_rights)"
    )
    content: str = Field(..., min_length=10, max_length=5000, description="Response content (10-5000 characters)")
    color: Optional[str] = Field("#000000", pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color code")

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Ensure content is not just whitespace."""
        if not v or not v.strip():
            raise ValueError('Content cannot be empty or only whitespace')
        return v.strip()

class MPResponse(MPResponseBase):
    """Schema for MP responses in debates."""
    id: int
    debate_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class VoteBase(BaseModel):
    """Schema for votes with validation."""
    mp_role: Literal["corporate", "academic", "government", "civil_rights"] = Field(
        ...,
        description="MP role casting the vote"
    )
    vote: Literal["for", "against", "abstain"] = Field(
        ...,
        description="Vote decision (must be: for, against, or abstain)"
    )
    reasoning: str = Field(..., min_length=10, max_length=2000, description="Reasoning for vote (10-2000 characters)")

    @field_validator('reasoning')
    @classmethod
    def validate_reasoning(cls, v: str) -> str:
        """Ensure reasoning is not just whitespace."""
        if not v or not v.strip():
            raise ValueError('Reasoning cannot be empty or only whitespace')
        return v.strip()

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
