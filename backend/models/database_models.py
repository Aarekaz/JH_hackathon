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
    status = Column(String(20), default='active', index=True)  # Index for filtering by status
    created_at = Column(DateTime, default=datetime.utcnow, index=True)  # Index for sorting by date

    # Foreign key to PolicyPaper
    paper_id = Column(Integer, ForeignKey('policy_papers.id'), index=True)  # Index for joins
    # Relationship with PolicyPaper
    paper = relationship("PolicyPaper", back_populates="debate")
    # Relationship with responses
    responses = relationship("MPResponse", back_populates="debate")
    votes = relationship("Vote", back_populates="debate")

class MPResponse(Base):
    """Database model for MP responses."""
    __tablename__ = "mp_responses"

    id = Column(Integer, primary_key=True, index=True)
    debate_id = Column(Integer, ForeignKey("debates.id"), index=True)  # Index for joins
    mp_role = Column(String, index=True)  # Index for filtering by role
    content = Column(Text)
    color = Column(String, default="#000000")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)  # Index for sorting

    # Relationship
    debate = relationship("Debate", back_populates="responses")

class Vote(Base):
    """Database model for votes."""
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    debate_id = Column(Integer, ForeignKey("debates.id"), index=True)  # Index for joins
    mp_role = Column(String, index=True)  # Index for filtering by role
    vote = Column(String, index=True)  # Index for vote aggregation queries
    reasoning = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)  # Index for sorting

    # Relationship
    debate = relationship("Debate", back_populates="votes")

class PolicyPaper(Base):
    """Database model for policy papers."""
    __tablename__ = "policy_papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    source = Column(String(50), default='arxiv', index=True)  # Index for filtering by source
    url = Column(Text)
    status = Column(String(20), default='pending', index=True)  # Index for filtering by status
    created_at = Column(DateTime, default=datetime.utcnow, index=True)  # Index for sorting

    # Relationship with Debate
    debate = relationship("Debate", back_populates="paper", uselist=False)
