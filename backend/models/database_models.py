from datetime import datetime

from db.database import Base
from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, Text,
                        func)
from sqlalchemy.orm import relationship


class Debate(Base):
    """Database model for debates."""
    __tablename__ = "debates"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    policy_text = Column(Text)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign key to PolicyPaper
    paper_id = Column(Integer, ForeignKey('policy_papers.id'))
    # Relationship with PolicyPaper
    paper = relationship("PolicyPaper", back_populates="debate")
    # Relationship with responses
    responses = relationship("MPResponse", back_populates="debate")
    votes = relationship("Vote", back_populates="debate")

class MPResponse(Base):
    """Database model for MP responses."""
    __tablename__ = "mp_responses"

    id = Column(Integer, primary_key=True, index=True)
    debate_id = Column(Integer, ForeignKey("debates.id"))
    mp_role = Column(String)
    content = Column(Text)
    color = Column(String, default="#000000")
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    debate = relationship("Debate", back_populates="responses")

class Vote(Base):
    """Database model for votes."""
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    debate_id = Column(Integer, ForeignKey("debates.id"))
    mp_role = Column(String)
    vote = Column(String)  # 'for', 'against', 'abstain'
    reasoning = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    debate = relationship("Debate", back_populates="votes")

class PolicyPaper(Base):
    """Database model for policy papers."""
    __tablename__ = "policy_papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    source = Column(String(50), default='arxiv')
    url = Column(Text)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with Debate
    debate = relationship("Debate", back_populates="paper", uselist=False)
