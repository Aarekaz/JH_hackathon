from datetime import datetime
from typing import Dict, List, Optional

from fastapi import HTTPException
from models.database_models import MPResponse
from openai import OpenAI


class OpenAIService:
    """Service for handling OpenAI API interactions."""
    
    def __init__(self, api_key: str = None):
        """Initialize OpenAI client with API key."""
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=api_key)
        
        self.mp_roles = {
            "corporate": {
                "description": "Represents business interests, focuses on innovation and economic growth",
                "bias": "Favors minimal regulation and market-driven solutions"
            },
            "government": {
                "description": "Represents state interests, focuses on governance and public safety",
                "bias": "Seeks balance between innovation and regulation"
            },
            "academic": {
                "description": "Represents research community, focuses on scientific evidence and ethics",
                "bias": "Emphasizes careful consideration of long-term implications"
            },
            "civil_rights": {
                "description": "Represents public interests, focuses on individual rights and fairness",
                "bias": "Advocates for transparency and protection of civil liberties"
            }
        }

    async def generate_mp_response(
        self, 
        role: str, 
        debate_topic: str, 
        debate_history: List[MPResponse]
    ) -> str:
        """Generate an MP's response based on their role and debate context."""
        try:
            # Format debate history for context
            formatted_history = "\n".join([
                f"{response.mp_role}: {response.content}" 
                for response in debate_history
            ])
            
            # Construct the prompt
            prompt = f"""You are an AI Member of Parliament representing {role} interests.
Role Description: {self.mp_roles[role]['description']}
Bias: {self.mp_roles[role]['bias']}

Debate Topic: {debate_topic}

Previous Discussion:
{formatted_history}

Please provide your response to the current debate, considering your role's perspective:"""

            # The OpenAI client is not async, so we don't use await here
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI MP in a parliamentary debate."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating MP response: {str(e)}"
            )

    async def evaluate_policy(self, policy_text: str) -> Dict:
        """Evaluate a proposed policy from multiple perspectives."""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI policy analyst."},
                    {"role": "user", "content": f"""Analyze this AI policy proposal from multiple perspectives:

Policy Text:
{policy_text}

Please provide:
1. Potential benefits
2. Potential risks
3. Implementation challenges
4. Stakeholder impacts"""}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return {
                "analysis": response.choices[0].message.content,
                "timestamp": datetime.utcnow()
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error evaluating policy: {str(e)}"
            )

    async def generate_vote_decision(
        self, 
        role: str, 
        debate_topic: str, 
        debate_history: List[MPResponse]
    ) -> dict:
        """Generate MP's voting decision based on the debate."""
        try:
            # Format debate history
            formatted_history = "\n".join([
                f"{response.mp_role}: {response.content[:200]}..." 
                for response in debate_history
            ])
            
            prompt = f"""As an AI MP representing {role} interests, analyze this debate and vote:
Topic: {debate_topic}

Key Points from Debate:
{formatted_history}

Based on your role's perspective and the debate, provide your vote and reasoning.
Format your response exactly as shown:
{{
    "vote": "for",  // must be exactly "for", "against", or "abstain"
    "reasoning": "Brief explanation of your vote"
}}"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI MP making a voting decision. Respond only with the exact JSON format specified."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200  # Limit response length
            )
            
            # Parse and validate response
            import json
            vote_data = json.loads(response.choices[0].message.content)
            
            # Validate vote value
            if vote_data["vote"] not in ["for", "against", "abstain"]:
                raise ValueError(f"Invalid vote value: {vote_data['vote']}")
                
            return vote_data

        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error parsing vote decision: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating vote decision: {str(e)}"
            )
