import logging
from typing import List

from db.database import get_db
from dependencies import get_arxiv_service, get_openai_service
from fastapi import APIRouter, Body, Depends, HTTPException
from models.database_models import Debate, PolicyPaper
from repositories.debate_repository import DebateRepository
from services.arxiv_service import ArxivService
from services.openai_service import OpenAIService
from sqlalchemy.orm import Session

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/papers", tags=["papers"])

@router.post("/arxiv/import", response_model=List[dict])
async def import_arxiv_papers(
    max_results: int = 10,
    db: Session = Depends(get_db),
    arxiv_service: ArxivService = Depends(get_arxiv_service)
):
    """Import papers from ArXiv."""
    try:
        # Fetch papers from ArXiv
        papers = await arxiv_service.fetch_ai_papers(max_results)
        
        stored_papers = []
        for paper_data in papers:
            paper = PolicyPaper(
                title=paper_data['title'],
                content=paper_data['summary'],
                summary=paper_data['summary'][:500],
                url=paper_data.get('url', ''),
                source='arxiv',
                status='pending'
            )
            db.add(paper)
            db.flush()
            stored_papers.append({
                "id": paper.id,
                "title": paper.title,
                "status": paper.status
            })
        
        db.commit()
        return stored_papers
        
    except Exception as e:
        logger.error(f"Error importing papers: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{paper_id}/debate")
async def start_debate(
    paper_id: int,
    db: Session = Depends(get_db),
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """Start a debate for a specific paper."""
    paper = db.query(PolicyPaper).filter(PolicyPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    debate_data = await openai_service.create_debate_from_paper(paper)
    
    debate = Debate(
        title=debate_data["debate_topic"],
        description=paper.summary,
        policy_text=paper.content,
        status="active",
        paper_id=paper.id
    )
    
    db.add(debate)
    paper.status = "debated"
    db.commit()
    
    return {
        "debate_id": debate.id,
        "debate_topic": debate.title,
        "status": debate.status
    }

@router.get("/{paper_id}", response_model=dict)
async def get_paper_details(
    paper_id: int,
    db: Session = Depends(get_db)
):
    """Get details of a specific policy paper."""
    try:
        paper = db.query(PolicyPaper).filter(PolicyPaper.id == paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        return {
            "id": paper.id,
            "title": paper.title,
            "content": paper.content,
            "summary": paper.summary,
            "source": paper.source,
            "url": paper.url,
            "status": paper.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
