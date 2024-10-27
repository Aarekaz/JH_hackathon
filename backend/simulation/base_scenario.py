from typing import Dict, Optional
from abc import ABC, abstractmethod

class BaseScenario(ABC):
    """Abstract base class for debate scenarios."""
    
    def __init__(self, name: str, description: str, policy_text: str):
        self.name = name
        self.description = description
        self.policy_text = policy_text
    
    @abstractmethod
    async def initialize(self, simulator) -> Dict:
        """Initialize the scenario with the simulator."""
        pass

