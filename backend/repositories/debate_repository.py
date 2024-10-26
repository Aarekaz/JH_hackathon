from sqlalchemy.orm import Session
from typing import List, Optional
from models.database_models import Debate, MPResponse, Vote
from models.schemas import DebateCreate

class DebateRepository:
    """Repository for database operations related to debates."""
    
    @staticmethod
    async def create_debate(db: Session, debate: DebateCreate) -> Debate:
        """Create a new debate in the database."""
        db_debate = Debate(
            title=debate.title,
            description=debate.description,
            policy_text=debate.policy_text
        )
        db.add(db_debate)
        db.commit()
        db.refresh(db_debate)
        return db_debate

    @staticmethod
    async def get_debate(db: Session, debate_id: int) -> Optional[Debate]:
        """Get a debate by ID."""
        return db.query(Debate).filter(Debate.id == debate_id).first()

    @staticmethod
    async def add_response(
        db: Session, 
        debate_id: int, 
        mp_role: str, 
        content: str
    ) -> MPResponse:
        """Add a new MP response to a debate."""
        db_response = MPResponse(
            debate_id=debate_id,
            mp_role=mp_role,
            content=content
        )
        db.add(db_response)
        db.commit()
        db.refresh(db_response)
        return db_response

    @staticmethod
    async def add_vote(
        db: Session, 
        debate_id: int, 
        mp_role: str, 
        vote: bool, 
        reasoning: str
    ) -> Vote:
        """Add a new vote to a debate."""
        db_vote = Vote(
            debate_id=debate_id,
            mp_role=mp_role,
            vote=vote,
            reasoning=reasoning
        )
        db.add(db_vote)
        db.commit()
        db.refresh(db_vote)
        return db_vote

    @staticmethod
    async def get_debate_responses(db: Session, debate_id: int) -> List[MPResponse]:
        """Get all responses for a debate."""
        return db.query(MPResponse).filter(MPResponse.debate_id == debate_id).all()

    @staticmethod
    async def create_vote(
        db: Session, 
        debate_id: int, 
        mp_role: str, 
        vote: str,
        reasoning: str
    ) -> Vote:
        db_vote = Vote(
            debate_id=debate_id,
            mp_role=mp_role,
            vote=vote,
            reasoning=reasoning
        )
        db.add(db_vote)
        db.commit()
        db.refresh(db_vote)
        return db_vote

    @staticmethod
    async def get_debate_votes(db: Session, debate_id: int) -> List[Vote]:
        return db.query(Vote).filter(Vote.debate_id == debate_id).all()
