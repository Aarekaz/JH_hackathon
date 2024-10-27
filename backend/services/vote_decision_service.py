import logging
from typing import Any, Dict, List, Optional

import numpy as np
from models.database_models import MPResponse


class VoteDecisionService:
    """Service for analyzing debate responses and making voting decisions."""
    
    def __init__(self):
        """Initialize the VoteDecisionService with aligned weights and role definitions."""
        self.role_definitions = {
            "corporate": {
                "description": "Represents business and industry interests",
                "bias": "Favors innovation and economic growth over strict regulation",
                "weights": {
                    "economic_impact": 0.8,
                    "innovation": 0.7,
                    "regulation": -0.6,
                    "social_impact": 0.3
                },
                "keywords": {
                    "positive": ["growth", "innovation", "efficiency", "market", "competitive"],
                    "negative": ["restriction", "limitation", "burden", "constraint"]
                }
            },
            "civil_rights": {
                "description": "Advocates for individual rights and privacy",
                "bias": "Prioritizes privacy and fairness over rapid advancement",
                "weights": {
                    "privacy": 0.8,
                    "fairness": 0.9,
                    "social_impact": 0.8,
                    "individual_rights": 0.9
                },
                "keywords": {
                    "positive": ["rights", "privacy", "protection", "fairness", "equality"],
                    "negative": ["surveillance", "discrimination", "bias"]
                }
            }
            # ... similar definitions for academic and government roles
        }
        
        # Keywords associated with different aspects
        self.aspect_keywords = {
            "economic_impact": ["cost", "economy", "market", "business", "financial"],
            "innovation": ["research", "development", "progress", "advancement"],
            "regulation": ["rules", "compliance", "standards", "requirements"],
            "social_impact": ["society", "community", "public", "people"],
            "privacy": ["privacy", "data", "personal", "surveillance"],
            "fairness": ["equality", "bias", "discrimination", "fair"],
            "implementation": ["implement", "deploy", "execute", "operate"]
        }

        self.role_weights = {
            "corporate": {
                "economic": 0.8,
                "innovation": 0.7,
                "regulation": -0.6,
                "market": 0.9
            },
            "academic": {
                "research": 0.9,
                "evidence": 0.8,
                "innovation": 0.7,
                "ethics": 0.6
            },
            "government": {
                "safety": 0.8,
                "regulation": 0.7,
                "economic": 0.5,
                "implementation": 0.6
            },
            "civil_rights": {
                "privacy": 0.9,
                "ethics": 0.8,
                "transparency": 0.7,
                "rights": 0.9
            }
        }

    def analyze_response_sentiment(self, content: str) -> Dict[str, float]:
        """Analyze response content for different aspects and their sentiment."""
        aspects_score = {}
        
        # Simple keyword-based scoring
        for aspect, keywords in self.aspect_keywords.items():
            score = 0
            word_count = len(content.split())
            
            for keyword in keywords:
                if keyword in content.lower():
                    # Count occurrences and normalize
                    occurrences = content.lower().count(keyword)
                    score += occurrences / word_count
            
            aspects_score[aspect] = score
        
        return aspects_score

    def calculate_vote_score(
        self, 
        role: str, 
        responses: List[MPResponse]
    ) -> Dict[str, Any]:
        """
        Calculate voting score based on role weights and response analysis.
        
        Args:
            role: The MP role calculating the vote
            responses: List of all debate responses
        
        Returns:
            Dict containing vote decision and confidence
        """
        try:
            # Get the current MP's response and other responses
            own_response = next((r for r in responses if r.mp_role == role), None)
            other_responses = [r for r in responses if r.mp_role != role]
            
            # Get role weights
            weights = self.role_weights.get(role, {})
            if not weights:
                return {"vote": "abstain", "confidence": 0.02}
            
            # Calculate sentiment scores
            total_score = 0.0
            if own_response:
                sentiment = self.analyze_response_sentiment(own_response.content)
                own_score = sum(
                    sentiment.get(aspect, 0) * weight 
                    for aspect, weight in weights.items()
                )
                total_score += own_score * 2  # Double weight for own response
                
            # Consider other responses
            for response in other_responses:
                sentiment = self.analyze_response_sentiment(response.content)
                score = sum(
                    sentiment.get(aspect, 0) * weight 
                    for aspect, weight in weights.items()
                )
                total_score += score
            
            # Normalize score
            final_score = np.tanh(total_score / (len(responses) + 1))
            
            # Determine vote
            if final_score > 0.3:
                vote = "for"
            elif final_score < -0.3:
                vote = "against"
            else:
                vote = "abstain"
                
            return {
                "vote": vote,
                "confidence": abs(final_score)
            }
            
        except Exception as e:
            logging.error(f"Error calculating vote for {role}: {str(e)}")
            return {"vote": "abstain", "confidence": 0.02}

    def _determine_vote(self, score: float) -> str:
        """Convert numerical score to vote decision."""
        if score > 0.3:
            return "for"
        elif score < -0.3:
            return "against"
        else:
            return "abstain"

    def calculate_vote_score(self, role: str, debate_history: List[Any]) -> Dict[str, Any]:
        """Calculate voting decision based on role and debate history."""
        try:
            # Default to neutral if no weights found
            weights = self.role_weights.get(role, {})
            if not weights:
                return {"vote": "abstain", "confidence": 0.02}

            # Simple scoring based on role weights
            score = sum(weights.values()) / len(weights)
            
            # Convert score to vote
            if score > 0.6:
                vote = "for"
            elif score < 0.4:
                vote = "against"
            else:
                vote = "abstain"
                
            return {
                "vote": vote,
                "confidence": abs(score - 0.5) * 2  # Scale confidence 0-1
            }
            
        except Exception as e:
            logging.error(f"Error calculating vote for {role}: {str(e)}")
            return {"vote": "abstain", "confidence": 0.02}
