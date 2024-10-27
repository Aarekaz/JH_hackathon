import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
from services.vote_decision_service import VoteDecisionService


@dataclass
class VoteMetric:
    """Stores vote consistency metrics."""
    debate_id: int
    mp_role: str
    response_sentiment: float
    vote_decision: str
    consistency_score: float
    timestamp: datetime

class VoteConsistencyMonitor:
    """Monitors and tracks vote consistency metrics."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics: List[VoteMetric] = []
    
    async def record_metric(
        self,
        debate_id: int,
        mp_role: str,
        response_content: str,
        vote_decision: Dict[str, any],
        vote_service: 'VoteDecisionService'
    ) -> float:
        """
        Record and analyze vote consistency.
        
        Args:
            debate_id: The debate identifier
            mp_role: The MP's role
            response_content: The MP's debate response
            vote_decision: The voting decision data
            vote_service: Instance of VoteDecisionService
            
        Returns:
            float: Consistency score between 0 and 1
        """
        # Analyze response sentiment using existing service
        response_analysis = vote_service.analyze_response_sentiment(response_content)
        
        # Calculate consistency score
        role_weights = vote_service.role_weights[mp_role]
        sentiment_score = sum(
            response_analysis.get(aspect, 0) * weight 
            for aspect, weight in role_weights.items()
        )
        
        # Compare sentiment with vote
        vote_value = {
            "for": 1.0,
            "against": -1.0,
            "abstain": 0.0
        }[vote_decision["vote"]]
        
        # Calculate consistency (1 = perfectly consistent, 0 = completely inconsistent)
        consistency = 1.0 - abs(
            (np.tanh(sentiment_score) - vote_value) / 2
        )
        
        # Store metric
        metric = VoteMetric(
            debate_id=debate_id,
            mp_role=mp_role,
            response_sentiment=sentiment_score,
            vote_decision=vote_decision["vote"],
            consistency_score=consistency,
            timestamp=datetime.utcnow()
        )
        self.metrics.append(metric)
        
        # Log if consistency is low
        if consistency < 0.5:
            self.logger.warning(
                f"Low vote consistency detected for {mp_role} in debate {debate_id}: {consistency:.2f}"
            )
        
        return consistency

    def get_metrics_summary(self) -> Dict[str, float]:
        """Get summary statistics of vote consistency."""
        if not self.metrics:
            return {"average_consistency": 0.0, "total_votes": 0}
            
        return {
            "average_consistency": sum(m.consistency_score for m in self.metrics) / len(self.metrics),
            "total_votes": len(self.metrics),
            "low_consistency_count": sum(1 for m in self.metrics if m.consistency_score < 0.5)
        }

