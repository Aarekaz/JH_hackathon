from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DebateCreate(BaseModel):
    """Schema for creating a new debate."""
    title: str
    description: str
    policy_text: str

class DebateResponse(BaseModel):
    """Schema for debate responses."""
    id: int
    title: str
    status: str
    created_at: datetime
    
class MPResponse(BaseModel):
    """Schema for MP responses in debates."""
    debate_id: int
    mp_role: str
    content: str
    timestamp: datetime

class Vote(BaseModel):
    """Schema for MP votes."""
    debate_id: int
    mp_role: str
    vote: bool
    reasoning: str

