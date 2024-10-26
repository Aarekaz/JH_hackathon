from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base
from sqlalchemy.sql import func

class Debate(Base):
    """Database model for debates."""
    __tablename__ = "debates"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    policy_text = Column(Text)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    responses = relationship("MPResponse", back_populates="debate")
    votes = relationship("Vote", back_populates="debate")

class MPResponse(Base):
    """Database model for MP responses."""
    __tablename__ = "mp_responses"

    id = Column(Integer, primary_key=True, index=True)
    debate_id = Column(Integer, ForeignKey("debates.id"))
    mp_role = Column(String)
    content = Column(Text)
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
