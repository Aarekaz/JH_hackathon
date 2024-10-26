import asyncio
import logging
import sys
import traceback
from datetime import datetime
from typing import Dict, List

import httpx

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParliamentSimulator:
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the simulator with base URL."""
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.mp_roles = ["corporate", "academic", "government", "civil_rights"]
        
    async def run_simulation(self):
        """Run the complete parliamentary simulation."""
        try:
            print("\n=== Starting AI Parliament Simulation ===\n")
            
            # 1. Import papers from ArXiv
            papers = await self.import_papers()
            if not papers:
                print("Error: No papers were imported!")
                return
                
            # 2. Select first paper and start debate
            first_paper = papers[0]
            print(f"\nStarting debate on paper: {first_paper['title']}")
            debate = await self.start_debate(first_paper['id'])
            
            # 3. Generate MP responses
            responses = await self.generate_mp_responses(debate['debate_id'])
            print(f"\nGenerated {len(responses)} MP responses")
            
            # 4. Cast votes
            votes = await self.cast_votes(debate['debate_id'])
            print(f"\nCollected {len(votes)} votes")
            
            # 5. Show final results
            await self.show_results(debate['debate_id'])
            
        except Exception as e:
            logger.error(f"Simulation failed: {str(e)}")
            traceback.print_exc()
        finally:
            await self.client.aclose()
    
    async def import_papers(self) -> List[Dict]:
        """Import papers from ArXiv."""
        try:
            logger.info("Importing papers from ArXiv...")
            response = await self.client.post(
                f"{self.base_url}/papers/arxiv/import",  # This matches the router endpoint
                params={"max_results": 3}
            )
            
            if response.status_code == 200:
                papers = response.json()
                if papers:
                    logger.info(f"Successfully imported {len(papers)} papers:")
                    for i, paper in enumerate(papers, 1):
                        logger.info(f"{i}. {paper['title']}")
                    return papers
                else:
                    logger.warning("No papers were imported")
                    return []
            else:
                logger.error(f"Error response: {response.text}")
                response.raise_for_status()
                
        except Exception as e:
            logger.error(f"Error importing papers: {str(e)}")
            raise
    
    async def start_debate(self, paper_id: int) -> Dict:
        """Start a debate on the selected paper."""
        print(f"\nStarting debate for paper ID: {paper_id}")
        response = await self.client.post(
            f"{self.base_url}/papers/{paper_id}/debate"
        )
        response.raise_for_status()
        debate = response.json()
        
        print(f"Debate created:")
        print(f"Topic: {debate['debate_topic']}")
        return debate
    
    async def generate_mp_responses(self, debate_id: int) -> List[Dict]:
        """Generate responses from all MPs."""
        print("\nGenerating MP responses...")
        responses = []
        
        for role in self.mp_roles:
            print(f"\nMP {role} is speaking...")
            response = await self.client.post(
                f"{self.base_url}/debates/{debate_id}/responses",
                params={"mp_role": role}
            )
            response.raise_for_status()
            mp_response = response.json()
            responses.append(mp_response)
            
            print(f"Response from {role}:")
            print(f"{mp_response['content']}")  # Remove truncation
            print("-" * 80)  # Add separator for readability
            
            await asyncio.sleep(1)
        
        return responses
    
    async def cast_votes(self, debate_id: int) -> List[Dict]:
        """Cast votes from all MPs."""
        print("\nCasting votes...")
        votes = []
        
        for role in self.mp_roles:
            print(f"\nMP {role} is voting...")
            response = await self.client.post(
                f"{self.base_url}/debates/{debate_id}/votes",
                params={"mp_role": role}
            )
            response.raise_for_status()
            vote = response.json()
            votes.append(vote)
            
            print(f"{role} voted: {vote['vote']}")
            print(f"Reasoning: {vote['reasoning']}")  # Remove truncation
            print("-" * 80)  # Add separator for readability
            
            await asyncio.sleep(1)
        
        return votes
    
    async def show_results(self, debate_id: int):
        """Show the final voting results."""
        print("\n=== Final Voting Results ===")
        
        response = await self.client.get(
            f"{self.base_url}/debates/{debate_id}/vote-summary"
        )
        response.raise_for_status()
        summary = response.json()
        
        print("\nVote Distribution:")
        print(f"For: {summary['for']}")
        print(f"Against: {summary['against']}")
        print(f"Abstain: {summary['abstain']}")
        print(f"\nFinal Result: Motion {summary['result'].upper()}")

async def main():
    """Main function to run the simulation."""
    try:
        simulator = ParliamentSimulator()
        await simulator.run_simulation()
    except Exception as e:
        logger.error(f"Simulation failed: {str(e)}", exc_info=True)
    finally:
        # Ensure client is closed
        if hasattr(simulator, 'client'):
            await simulator.client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
