from typing import List, Optional
from pydantic import BaseModel

class MPProfile(BaseModel):
    role: str
    objectives: List[str]
    bias_factors: List[str]
    voting_weights: dict

