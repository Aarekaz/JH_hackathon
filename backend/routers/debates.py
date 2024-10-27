from typing import List

from db.database import get_db
from dependencies import get_openai_service
from fastapi import APIRouter, Depends, HTTPException
from models.database_models import PolicyPaper
from models.schemas import DebateCreate, DebateResponse, MPResponse, Vote
from repositories.debate_repository import DebateRepository
from services.openai_service import OpenAIService
from sqlalchemy.orm import Session

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

@router.post("/{paper_id}/start-full-debate")
async def start_full_debate(
    paper_id: int,
    db: Session = Depends(get_db),
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """Start a debate and generate all MP responses and votes."""
    try:
        # Get the paper and create debate
        paper = db.query(PolicyPaper).filter(PolicyPaper.id == paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Create the debate
        debate_data = await openai_service.create_debate_from_paper(paper)
        debate = await DebateRepository.create_debate_from_paper(db, paper, debate_data)
        
        # Generate responses for all MP roles
        mp_roles = ["corporate", "academic", "government", "civil_rights"]
        db_responses = []  # Store actual MPResponse objects
        response_dicts = []  # Store dictionary representations
        
        for role in mp_roles:
            # Get MP color from OpenAI service
            mp_color = openai_service.mp_roles[role]["color"]
            
            content = await openai_service.generate_mp_response(
                role,
                debate.title,
                db_responses  # Pass the list of MPResponse objects
            )
            
            db_response = await DebateRepository.add_response(
                db,
                debate.id,
                role,
                content,
                mp_color
            )
            db_responses.append(db_response)
            
            # Convert to dict for API response
            response_dicts.append({
                "id": db_response.id,
                "debate_id": db_response.debate_id,
                "mp_role": db_response.mp_role,
                "content": db_response.content,
                "color": db_response.color,
                "timestamp": db_response.timestamp
            })
        
        # Generate votes using the actual responses
        votes = []
        for role in mp_roles:
            vote_decision = await openai_service.generate_vote_decision(
                role,
                debate.title,
                db_responses  # Pass the actual MPResponse objects
            )
            vote = await DebateRepository.create_vote(
                db,
                debate.id,
                role,
                vote_decision["vote"],
                vote_decision["reasoning"]
            )
            votes.append(vote)
        
        # Get vote summary
        summary = await get_vote_summary(debate.id, db)
        
        return {
            "debate_id": debate.id,
            "title": debate.title,
            "responses": response_dicts,
            "votes": votes,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in debate process: {str(e)}"
        )
