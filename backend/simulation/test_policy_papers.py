import requests
import asyncio
from typing import Dict, List
import sys

BASE_URL = "http://localhost:8000"

async def test_policy_papers():
    try:
        # Import ArXiv papers
        response = requests.post(
            f"{BASE_URL}/papers/arxiv/import",
            params={"max_results": 3}
        )
        response.raise_for_status()
        
        papers = response.json()
        print("\nImported ArXiv Papers:")
        for paper in papers:
            print(f"- {paper['title']} (ID: {paper['id']})")
        
        if not papers:
            print("No papers were imported!")
            sys.exit(1)
            
        # Create custom paper
        custom_paper = {
            "title": "AI Safety Guidelines 2024",
            "content": "This paper proposes new safety guidelines...",
            "summary": "A comprehensive framework for AI safety"
        }
        
        response = requests.post(
            f"{BASE_URL}/papers/custom",
            json=custom_paper
        )
        response.raise_for_status()
        custom_paper_response = response.json()
        print("\nCreated Custom Paper:", custom_paper_response)
        
        # Start debate on first ArXiv paper
        first_paper_id = papers[0]["id"]
        print(f"\nStarting debate for paper ID: {first_paper_id}")
        response = requests.post(f"{BASE_URL}/papers/{first_paper_id}/debate")
        response.raise_for_status()
        print("\nCreated Debate:", response.json())
        
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Server response: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_policy_papers())
