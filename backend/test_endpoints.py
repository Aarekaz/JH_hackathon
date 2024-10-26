import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"

def test_endpoints():
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

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("\nWarning: OPENAI_API_KEY not set. Running with test responses.")
    test_endpoints()
