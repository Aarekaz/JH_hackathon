import json
import os
from datetime import datetime
import asyncio

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"

async def test_endpoints():
    # 1. Create a debate
    debate_data = {
        "title": "AI Safety Regulations",
        "description": "Should we implement strict regulations on AI development?",
        "policy_text": "Proposed policy: All AI models above certain capabilities must undergo safety audits."
    }
    
    response = requests.post(f"{BASE_URL}/debates/", json=debate_data)
    print("\n1. Create Debate Response:", response.json())
    debate_id = response.json()["id"]
    
    # 2. Get debate details
    response = requests.get(f"{BASE_URL}/debates/{debate_id}")
    print("\n2. Get Debate Details:", response.json())
    
    # 3. Add responses from different MP roles
    mp_roles = ["corporate", "academic", "government", "civil_rights"]
    
    for role in mp_roles:
        # Add a manual response if OpenAI key is not set
        if not os.getenv("OPENAI_API_KEY"):
            response = requests.post(
                f"{BASE_URL}/debates/{debate_id}/responses",
                params={"mp_role": role, "content": f"Test response from {role} perspective"}
            )
        else:
            response = requests.post(
                f"{BASE_URL}/debates/{debate_id}/responses",
                params={"mp_role": role}
            )
        
        print(f"\n3. {role.capitalize()} MP Response:", response.json())
        
        # Add a small delay between requests
        import time
        time.sleep(1)
    
    # 4. Get all responses
    response = requests.get(f"{BASE_URL}/debates/{debate_id}/responses")
    print("\n4. All Debate Responses:", response.json())

    # Test voting
    print("\nTesting Voting Process:")
    for role in ["corporate", "academic", "government", "civil_rights"]:
        try:
            response = requests.post(
                f"{BASE_URL}/debates/{debate_id}/votes",
                params={"mp_role": role}
            )
            response.raise_for_status()  # Raise exception for bad status codes
            vote_data = response.json()
            print(f"\n{role.capitalize()} Vote:")
            print(f"Decision: {vote_data['vote']}")
            print(f"Reasoning: {vote_data['reasoning']}")
        except Exception as e:
            print(f"Error getting {role} vote:", str(e))

    # Get vote summary
    try:
        response = requests.get(f"{BASE_URL}/debates/{debate_id}/vote-summary")
        response.raise_for_status()
        print("\nVote Summary:", response.json())
    except Exception as e:
        print("Error getting vote summary:", str(e))

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_endpoints())
