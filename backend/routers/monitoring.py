from datetime import datetime, timedelta
from typing import Dict, List

from db.database import get_db
from dependencies import get_vote_monitor  # Add this import
from fastapi import APIRouter, Depends
from models.schemas import DebateMetrics, VoteDistribution
from monitoring.vote_metrics import VoteConsistencyMonitor
from sqlalchemy.orm import Session

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@router.get("/vote-consistency")
async def get_vote_consistency_metrics(
    time_window: str = "24h",
    vote_monitor: VoteConsistencyMonitor = Depends(get_vote_monitor)
) -> Dict[str, float]:
    """
    Get vote consistency metrics for a specific time window.
    
    Args:
        time_window: Time window for metrics (24h, 7d, 30d)
        vote_monitor: Vote consistency monitoring service
        
    Returns:
        Dict containing consistency metrics
    """
    # Calculate time threshold
    now = datetime.utcnow()
    time_thresholds = {
        "24h": now - timedelta(hours=24),
        "7d": now - timedelta(days=7),
        "30d": now - timedelta(days=30)
    }
    threshold = time_thresholds.get(time_window, time_thresholds["24h"])
    
    # Filter metrics by time window
    relevant_metrics = [
        m for m in vote_monitor.metrics 
        if m.timestamp >= threshold
    ]
    
    if not relevant_metrics:
        return {
            "average_consistency": 0.0,
            "total_votes": 0,
            "low_consistency_count": 0,
            "time_window": time_window
        }
    
    # Calculate metrics
    return {
        "average_consistency": sum(m.consistency_score for m in relevant_metrics) / len(relevant_metrics),
        "total_votes": len(relevant_metrics),
        "low_consistency_count": sum(1 for m in relevant_metrics if m.consistency_score < 0.5),
        "time_window": time_window
    }

@router.get("/role-metrics")
async def get_role_metrics(
    vote_monitor: VoteConsistencyMonitor = Depends(get_vote_monitor)
) -> Dict[str, Dict[str, float]]:
    """Get voting metrics broken down by MP role."""
    role_metrics = {}
    
    for role in ["corporate", "academic", "government", "civil_rights"]:
        role_votes = [m for m in vote_monitor.metrics if m.mp_role == role]
        if role_votes:
            role_metrics[role] = {
                "average_consistency": sum(v.consistency_score for v in role_votes) / len(role_votes),
                "total_votes": len(role_votes),
                "low_consistency_votes": sum(1 for v in role_votes if v.consistency_score < 0.5)
            }
        else:
            role_metrics[role] = {
                "average_consistency": 0.0,
                "total_votes": 0,
                "low_consistency_votes": 0
            }
    
    return role_metrics

@router.get("/debate-metrics/{debate_id}", response_model=DebateMetrics)
async def get_debate_metrics(
    debate_id: int,
    vote_monitor: VoteConsistencyMonitor = Depends(get_vote_monitor)
) -> DebateMetrics:
    """Get detailed metrics for a specific debate."""
    debate_metrics = [m for m in vote_monitor.metrics if m.debate_id == debate_id]
    
    if not debate_metrics:
        return DebateMetrics(
            debate_id=debate_id,
            average_consistency=0.0,
            votes_by_role={role: 0 for role in ["corporate", "academic", "government", "civil_rights"]},
            vote_decisions=VoteDistribution(for_votes=0, against_votes=0, abstain_votes=0),
            metrics=None,
            message="No metrics found for this debate"
        )
    
    return DebateMetrics(
        debate_id=debate_id,
        average_consistency=sum(m.consistency_score for m in debate_metrics) / len(debate_metrics),
        votes_by_role={
            role: len([m for m in debate_metrics if m.mp_role == role])
            for role in ["corporate", "academic", "government", "civil_rights"]
        },
        vote_decisions=VoteDistribution(
            for_votes=len([m for m in debate_metrics if m.vote_decision == "for"]),
            against_votes=len([m for m in debate_metrics if m.vote_decision == "against"]),
            abstain_votes=len([m for m in debate_metrics if m.vote_decision == "abstain"])
        )
    )
