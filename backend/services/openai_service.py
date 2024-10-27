import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from models.database_models import MPResponse, PolicyPaper
from openai import OpenAI
from services.vote_decision_service import VoteDecisionService
import logging


class OpenAIService:
    """Service for handling OpenAI API interactions."""
    
    def __init__(self, api_key: str = None):
        """Initialize OpenAI client with API key."""
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=api_key)
        
        self.mp_roles = {
            "corporate": {
                "description": "Represents business and industry interests",
                "bias": "Favors market-driven solutions and minimal regulation",
                "color": "#DA0211"  # Business blue
            },
            "academic": {
                "description": "Represents academic and research institutions",
                "bias": "Favors evidence-based policy and thorough research",
                "color": "#FDA003"  # Academic purple
            },
            "government": {
                "description": "Represents governmental and regulatory interests",
                "bias": "Favors structured oversight and public safety",
                "color": "#2CAFFE"  # Government green
            },
            "civil_rights": {
                "description": "Represents civil society and individual rights",
                "bias": "Favors privacy and individual protections",
                "color": "#000099"  # Advocacy red
            }
        }

        self.vote_service = VoteDecisionService()

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
                model="gpt-4o-mini",
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
                model="gpt-4o-mini",
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
            # Calculate vote score using the new service
            vote_analysis = self.vote_service.calculate_vote_score(role, debate_history)
            
            # Use GPT to generate reasoning based on the vote
            prompt = f"""As an AI MP representing {role} interests, explain this voting decision:
            Topic: {debate_topic}
            Vote: {vote_analysis['vote']}
            Confidence: {vote_analysis['confidence']:.2f}
            
            Provide a convincing explanation for this voting decision from your role's perspective.
            """

            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an AI MP explaining your voting decision."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=200
                )
                reasoning = response.choices[0].message.content
            except Exception as e:
                logging.error(f"OpenAI API error for {role}: {str(e)}")
                # Provide a fallback reasoning if OpenAI fails
                reasoning = f"As a {role} representative, I have considered the implications and reached this decision."
            
            return {
                "vote": vote_analysis['vote'],
                "reasoning": reasoning,
                "confidence": vote_analysis['confidence']
            }
            
        except Exception as e:
            logging.error(f"Vote generation error for {role}: {str(e)}")
            # Return a default vote instead of raising an exception
            return {
                "vote": "abstain",
                "reasoning": f"Due to technical difficulties, as a {role} representative, I must abstain from voting.",
                "confidence": 0.0
            }

    async def create_debate_from_paper(self, paper: PolicyPaper) -> dict:
        """Create a structured debate from a policy paper."""
        try:
            prompt = f"""Based on this AI research paper, create a debate topic:
Title: {paper.title}
Summary: {paper.summary}

Create a debate topic that MPs can discuss regarding AI policy implications."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a parliamentary debate moderator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            # Always return a structured response, even if OpenAI fails
            try:
                content = response.choices[0].message.content
            except:
                content = paper.title

            return {
                "debate_topic": content,
                "background": paper.summary,
                "key_considerations": ["Safety", "Ethics", "Implementation"]
            }
            
        except Exception as e:
            print(f"OpenAI Error: {str(e)}")
            # Return a fallback response instead of raising an error
            return {
                "debate_topic": f"Policy Implications of: {paper.title}",
                "background": paper.summary,
                "key_considerations": ["Safety", "Ethics", "Implementation"]
            }

    async def validate_vote_consistency(
        self,
        role: str,
        response_content: str,
        vote_decision: Dict[str, Any]
    ) -> bool:
        """
        Validate that the voting decision is consistent with the MP's debate response.
        
        Args:
            role: The MP role
            response_content: The MP's debate response
            vote_decision: The generated vote decision
        
        Returns:
            bool: True if consistent, False otherwise
        """
        try:
            prompt = f"""Analyze if this MP's voting decision is consistent with their debate response:
            
            Role: {role}
            Debate Response: {response_content}
            Vote: {vote_decision['vote']}
            Reasoning: {vote_decision['reasoning']}
            
            Is this vote consistent with the position expressed in the debate? Answer only YES or NO."""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are analyzing voting consistency."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            return "YES" in response.choices[0].message.content.upper()
            
        except Exception as e:
            logging.warning(f"Consistency check failed: {str(e)}")
            return True  # Default to accepting the vote if check fails
