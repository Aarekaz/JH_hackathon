from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from models.schemas import DebateCreate, DebateResponse, MPResponse, Vote
from repositories.debate_repository import DebateRepository
from db.database import get_db
from dependencies import get_openai_service
from services.openai_service import OpenAIService

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
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """Cast a vote for a specific MP role."""
    try:
        # Get debate details and history
        debate = await DebateRepository.get_debate(db, debate_id)
        if not debate:
            raise HTTPException(status_code=404, detail="Debate not found")
            
        debate_history = await DebateRepository.get_debate_responses(db, debate_id)
        
        # Generate vote decision
        vote_decision = await openai_service.generate_vote_decision(
            mp_role,
            debate.title,
            debate_history
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
            "timestamp": db_vote.timestamp
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
):
    """Get a summary of the voting results."""
    votes = await DebateRepository.get_debate_votes(db, debate_id)
    
    summary = {
        "for": 0,
        "against": 0,
        "abstain": 0,
        "total": len(votes),
        "result": None
    }
    
    for vote in votes:
        summary[vote.vote] += 1
    
    # Determine result
    if summary["for"] > summary["against"]:
        summary["result"] = "passed"
    elif summary["for"] < summary["against"]:
        summary["result"] = "rejected"
    else:
        summary["result"] = "tied"
    
    return summary
