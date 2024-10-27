import asyncio
import logging
from typing import Dict, List, Optional

import httpx
from simulation.base_scenario import BaseScenario

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParliamentSimulator:
    """Main simulator class for AI Parliament debates."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.mp_roles = ["corporate", "academic", "government", "civil_rights"]

    async def run(self, scenario: BaseScenario) -> Dict:
        """Run a simulation with the given scenario."""
        try:
            logger.info(f"Starting simulation: {scenario.name}")
            
            # Initialize debate
            debate = await scenario.initialize(self)
            if not debate:
                raise ValueError("Failed to initialize debate")
            
            # Generate responses
            responses = await self.generate_mp_responses(debate['id'])
            
            # Cast votes
            votes = await self.cast_votes(debate['id'])
            
            # Get results
            results = await self.get_debate_results(debate['id'])
            
            return {
                "debate": debate,
                "responses": responses,
                "votes": votes,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Simulation failed: {str(e)}")
            raise
        finally:
            await self.client.aclose()

    async def generate_mp_responses(self, debate_id: int) -> List[Dict]:
        """Generate responses from all MPs."""
        logger.info("Generating MP responses...")
        responses = []
        
        for role in self.mp_roles:
            logger.info(f"MP {role} is speaking...")
            response = await self.client.post(
                f"{self.base_url}/debates/{debate_id}/responses",
                params={"mp_role": role}
            )
            response.raise_for_status()
            mp_response = response.json()
            responses.append(mp_response)
            await asyncio.sleep(1)
        
        return responses

    async def cast_votes(self, debate_id: int) -> List[Dict]:
        """Cast votes from all MPs."""
        logger.info("Casting votes...")
        votes = []
        
        for role in self.mp_roles:
            logger.info(f"MP {role} is voting...")
            response = await self.client.post(
                f"{self.base_url}/debates/{debate_id}/votes",
                params={"mp_role": role}
            )
            response.raise_for_status()
            vote = response.json()
            votes.append(vote)
            await asyncio.sleep(1)
        
        return votes

    async def get_debate_results(self, debate_id: int) -> Dict:
        """Get the final voting results."""
        logger.info("Getting debate results...")
        response = await self.client.get(
            f"{self.base_url}/debates/{debate_id}/vote-summary"
        )
        response.raise_for_status()
        return response.json()
