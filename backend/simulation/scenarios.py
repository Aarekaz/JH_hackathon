from abc import ABC, abstractmethod
from typing import Dict, Optional

from simulation.simulator import ParliamentSimulator
from simulation.base_scenario import BaseScenario


class DebateScenario(BaseScenario):
    """Concrete implementation of a debate scenario."""
    
    async def initialize(self, simulator) -> Dict:
        """Initialize a debate with this scenario."""
        debate_data = {
            "title": self.name,
            "description": self.description,
            "policy_text": self.policy_text
        }
        
        response = await simulator.client.post(
            f"{simulator.base_url}/debates/",
            json=debate_data
        )
        response.raise_for_status()
        return response.json()


class ArxivDebateScenario(DebateScenario):
    """Scenario for debates based on ArXiv papers."""
    
    def __init__(self, max_papers: int = 3):
        super().__init__("ArXiv Paper Debate")
        self.max_papers = max_papers
    
    async def initialize(self, simulator: 'ParliamentSimulator') -> Dict:
        # Import papers
        response = await simulator.client.post(
            f"{simulator.base_url}/papers/arxiv/import",
            params={"max_results": self.max_papers}
        )
        papers = response.json()
        
        if not papers:
            raise ValueError("No papers imported")
            
        # Start debate with first paper
        response = await simulator.client.post(
            f"{simulator.base_url}/papers/{papers[0]['id']}/debate"
        )
        return response.json()

class CustomDebateScenario(DebateScenario):
    """Scenario for custom debate topics."""
    
    def __init__(self, topic: str, description: str):
        super().__init__("Custom Topic Debate")
        self.topic = topic
        self.description = description
    
    async def initialize(self, simulator: 'ParliamentSimulator') -> Dict:
        debate_data = {
            "title": self.topic,
            "description": self.description,
            "policy_text": f"Policy implications of: {self.topic}"
        }
        
        response = await simulator.client.post(
            f"{simulator.base_url}/debates/",
            json=debate_data
        )
        return response.json()
