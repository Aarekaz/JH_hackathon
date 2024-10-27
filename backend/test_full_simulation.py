import asyncio
from datetime import datetime
from typing import Dict, List

import httpx
import pytest
from models.schemas import DebateMetrics, VoteDistribution
from monitoring.vote_metrics import VoteConsistencyMonitor
from simulation.simulator import ParliamentSimulator


class TestScenario:
    def __init__(self, name: str, policy_text: str):
        self.name = name
        self.policy_text = policy_text
        
    async def initialize(self, simulator: ParliamentSimulator) -> Dict:
        """Initialize a debate with this scenario."""
        debate_data = {
            "title": self.name,
            "description": f"Debate on: {self.name}",
            "policy_text": self.policy_text
        }
        
        response = await simulator.client.post(
            f"{simulator.base_url}/debates/",
            json=debate_data
        )
        response.raise_for_status()
        return response.json()

async def test_full_debate_cycle():
    """Test a complete debate cycle with monitoring."""
    # Initialize simulator
    simulator = ParliamentSimulator(base_url="http://localhost:8000")
    
    # Create test scenario
    scenario = TestScenario(
        name="AI Safety Regulations",
        policy_text="All AI models above certain capabilities must undergo safety audits."
    )
    
    try:
        # Run simulation
        results = await simulator.run(scenario)
        debate_id = results["debate"]["id"]
        
        # Verify debate creation
        assert results["debate"]["title"] == scenario.name
        
        # Verify MP responses
        assert len(results["responses"]) == 4  # One for each role
        for response in results["responses"]:
            assert response["mp_role"] in simulator.mp_roles
            assert response["content"]  # Should have content
            
        # Verify votes
        assert len(results["votes"]) == 4  # One vote per MP
        for vote in results["votes"]:
            assert vote["vote"] in ["for", "against", "abstain"]
            assert vote["reasoning"]  # Should have reasoning
            
        # Check monitoring metrics
        async with httpx.AsyncClient() as client:
            # Get debate metrics
            response = await client.get(
                f"{simulator.base_url}/monitoring/debate-metrics/{debate_id}"
            )
            metrics = DebateMetrics(**response.json())
            
            # Verify metrics structure
            assert metrics.debate_id == debate_id
            assert isinstance(metrics.average_consistency, float)
            assert all(role in metrics.votes_by_role for role in simulator.mp_roles)
            
            # Get role metrics
            response = await client.get(
                f"{simulator.base_url}/monitoring/role-metrics"
            )
            role_metrics = response.json()
            
            # Verify role metrics
            for role in simulator.mp_roles:
                assert role in role_metrics
                assert "average_consistency" in role_metrics[role]
                assert "total_votes" in role_metrics[role]
                
        print("\nSimulation Results:")
        print(f"Debate ID: {debate_id}")
        print(f"Average Consistency: {metrics.average_consistency:.2f}")
        print("\nVotes by Role:")
        for role, count in metrics.votes_by_role.items():
            print(f"{role}: {count}")
        print("\nVote Distribution:")
        print(f"For: {metrics.vote_decisions.for_votes}")
        print(f"Against: {metrics.vote_decisions.against_votes}")
        print(f"Abstain: {metrics.vote_decisions.abstain_votes}")
        
    finally:
        await simulator.client.aclose()

if __name__ == "__main__":
    asyncio.run(test_full_debate_cycle())
