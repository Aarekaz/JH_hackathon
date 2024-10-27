from typing import Any, Dict, List

from db.database import get_db
from dependencies import get_openai_service, get_vote_monitor
from fastapi import APIRouter, Depends, HTTPException
from models.database_models import PolicyPaper
from models.schemas import DebateCreate, DebateResponse, MPResponse, Vote, VoteResponse
from monitoring.vote_metrics import VoteConsistencyMonitor
from repositories.debate_repository import DebateRepository
from services.openai_service import OpenAIService
from sqlalchemy.orm import Session
import logging

router = APIRouter(prefix="/debates", tags=["debates"])

@router.post("/", response_model=DebateResponse)
async def create_debate(
    debate: DebateCreate, 
    db: Session = Depends(get_db)
):
    """Create a new debate session."""
    try:
        return await DebateRepository.create_debate(db, debate)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{debate_id}", response_model=DebateResponse)
async def get_debate(
    debate_id: int, 
    db: Session = Depends(get_db)
):
    """Get details of a specific debate."""
    debate = await DebateRepository.get_debate(db, debate_id)
    if not debate:
        raise HTTPException(status_code=404, detail="Debate not found")
    return debate

@router.post("/{debate_id}/responses", response_model=MPResponse)
async def add_mp_response(
    debate_id: int,
    mp_role: str,  # Changed from body to query parameter
    content: str = None,  # Optional content
    db: Session = Depends(get_db),
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """Add an AI-generated MP response to the debate."""
    try:
        debate = await DebateRepository.get_debate(db, debate_id)
        if not debate:
            raise HTTPException(status_code=404, detail="Debate not found")
            
        debate_history = await DebateRepository.get_debate_responses(db, debate_id)
        
        # Generate AI response if no content provided
        if content is None:
            content = await openai_service.generate_mp_response(
                mp_role,
                debate.title,
                debate_history
            )
        
        return await DebateRepository.add_response(db, debate_id, mp_role, content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{debate_id}/responses", response_model=List[MPResponse])
async def get_debate_responses(
    debate_id: int,
    db: Session = Depends(get_db)
):
    """Get all responses for a debate."""
    try:
        return await DebateRepository.get_debate_responses(db, debate_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{debate_id}/votes", response_model=dict)
async def cast_vote(
    debate_id: int,
    mp_role: str,
    db: Session = Depends(get_db),
    openai_service: OpenAIService = Depends(get_openai_service),
    vote_monitor: VoteConsistencyMonitor = Depends(get_vote_monitor)
):
    """Cast a vote for a specific MP role."""
    try:
        # Get debate details and history
        debate = await DebateRepository.get_debate(db, debate_id)
        if not debate:
            raise HTTPException(status_code=404, detail="Debate not found")
            
        debate_history = await DebateRepository.get_debate_responses(db, debate_id)
        mp_response = next((r for r in debate_history if r.mp_role == mp_role), None)
        
        # Generate vote decision
        vote_decision = await openai_service.generate_vote_decision(
            mp_role,
            debate.title,
            debate_history
        )
        
        # Monitor vote consistency if we have an MP response
        consistency_score = None
        if mp_response:
            consistency_score = await vote_monitor.record_metric(
                debate_id,
                mp_role,
                mp_response.content,
                vote_decision,
                openai_service.vote_service
            )
        
        # Store vote in database
        db_vote = await DebateRepository.create_vote(
            db,
            debate_id=debate_id,
            mp_role=mp_role,
            vote=vote_decision["vote"],
            reasoning=vote_decision["reasoning"]
        )
        
        return {
            "status": "success",
            "vote": db_vote.vote,
            "reasoning": db_vote.reasoning,
            "mp_role": db_vote.mp_role,
            "debate_id": db_vote.debate_id,
            "timestamp": db_vote.timestamp,
            "consistency_score": consistency_score
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error casting vote: {str(e)}"
        )

@router.get("/{debate_id}/votes", response_model=List[Vote])
async def get_votes(
    debate_id: int,
    db: Session = Depends(get_db)
):
    """Get all votes for a debate."""
    return await DebateRepository.get_debate_votes(db, debate_id)

@router.get("/{debate_id}/vote-summary")
async def get_vote_summary(
    debate_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a summary of the voting results.
    
    Args:
        debate_id: The ID of the debate
        db: Database session
        
    Returns:
        Dict containing vote counts and final result
    """
    votes = await DebateRepository.get_debate_votes(db, debate_id)
    
    summary: Dict[str, Any] = {
        "for": 0,
        "against": 0,
        "abstain": 0,
        "total": len(votes),
        "result": None
    }
    
    for vote in votes:
        summary[vote.vote] += 1
    
    # Calculate voting result
    if summary["abstain"] == summary["total"]:
        summary["result"] = "abstained"
    else:
        # Only consider non-abstaining votes for the result
        total_votes = summary["for"] + summary["against"]
        if total_votes > 0:
            # Calculate if we have a majority
            if summary["for"] > total_votes / 2:
                summary["result"] = "passed"
            elif summary["against"] > total_votes / 2:
                summary["result"] = "rejected"
            else:
                summary["result"] = "tied"
        else:
            summary["result"] = "abstained"
    
    return summary

@router.post("/{paper_id}/start-full-debate")
async def start_full_debate(
    paper_id: int,
    db: Session = Depends(get_db),
    openai_service: OpenAIService = Depends(get_openai_service)
) -> Dict[str, Any]:
    """
    Start a debate and generate all MP responses and votes.
    
    Args:
        paper_id: ID of the policy paper
        db: Database session
        openai_service: OpenAI service instance
        
    Returns:
        Dict containing debate details, responses, votes and summary
        
    Raises:
        HTTPException: If paper not found or debate creation fails
    """
    try:
        # Get the paper and create debate
        paper = db.query(PolicyPaper).filter(PolicyPaper.id == paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Create the debate with better error handling
        try:
            debate_data = await openai_service.create_debate_from_paper(paper)
            debate = await DebateRepository.create_debate_from_paper(db, paper, debate_data)
        except Exception as e:
            logging.error(f"Failed to create debate: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create debate")
        
        # Generate responses for all MP roles
        mp_roles = ["corporate", "academic", "government", "civil_rights"]
        db_responses: List[MPResponse] = []
        response_dicts: List[Dict[str, Any]] = []
        
        for role in mp_roles:
            try:
                mp_color = openai_service.mp_roles[role]["color"]
                content = await openai_service.generate_mp_response(
                    role,
                    debate.title,
                    db_responses
                )
                
                db_response = await DebateRepository.add_response(
                    db,
                    debate.id,
                    role,
                    content,
                    mp_color
                )
                db_responses.append(db_response)
                
                response_dicts.append({
                    "id": db_response.id,
                    "debate_id": db_response.debate_id,
                    "mp_role": db_response.mp_role,
                    "content": db_response.content,
                    "color": db_response.color,
                    "timestamp": db_response.timestamp
                })
            except Exception as e:
                logging.error(f"Failed to generate response for {role}: {str(e)}")
                continue
        
        # Generate votes with error handling
        votes = []
        for role in mp_roles:
            try:
                vote_decision = await openai_service.generate_vote_decision(
                    role,
                    debate.title,
                    db_responses
                )
                db_vote = await DebateRepository.create_vote(
                    db,
                    debate.id,
                    role,
                    vote_decision["vote"],
                    vote_decision["reasoning"]
                )
                # Convert DB model to Pydantic model
                vote_response = VoteResponse.from_orm(db_vote)
                votes.append(vote_response)
            except Exception as e:
                logging.error(f"Failed to generate vote for {role}: {str(e)}")
                continue
        
        # Get vote summary
        try:
            summary = await get_vote_summary(debate.id, db)
        except Exception as e:
            logging.error(f"Failed to generate vote summary: {str(e)}")
            summary = {"error": "Failed to generate summary"}
        
        return {
            "debate_id": debate.id,
            "title": debate.title,
            "responses": response_dicts,
            "votes": [vote.model_dump() for vote in votes],  # Convert to dict
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in debate process: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in debate process: {str(e)}"
        )
