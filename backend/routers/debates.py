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

@router.post("/{debate_id}/votes", response_model=Vote)
async def submit_vote(debate_id: int, vote: Vote):
    """Submit an MP's vote on a debate."""
    try:
        # Implementation for vote submission
        return vote
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
