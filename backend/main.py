from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel
from routers import debates, moderator
from sqlalchemy.orm import Session
from db.database import get_db, engine
from models.database_models import Base, Debate, MPResponse

app = FastAPI(title="AI Parliament API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(debates.router)
app.include_router(moderator.router)

# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/debates/")
async def create_debate(title: str, description: str, db: Session = Depends(get_db)):
    """Create a new debate."""
    debate = Debate(title=title, description=description)
    db.add(debate)
    db.commit()
    db.refresh(debate)
    return debate

@app.get("/debates/")
async def list_debates(db: Session = Depends(get_db)):
    """List all debates."""
    return db.query(Debate).all()

@app.post("/debates/{debate_id}/responses/")
async def add_response(
    debate_id: int, 
    mp_role: str, 
    content: str, 
    db: Session = Depends(get_db)
):
    """Add an MP response to a debate."""
    # Check if debate exists
    debate = db.query(Debate).filter(Debate.id == debate_id).first()
    if not debate:
        raise HTTPException(status_code=404, detail="Debate not found")
    
    response = MPResponse(
        debate_id=debate_id,
        mp_role=mp_role,
        content=content
    )
    db.add(response)
    db.commit()
    db.refresh(response)
    return response

@app.get("/debates/{debate_id}/responses/")
async def get_debate_responses(debate_id: int, db: Session = Depends(get_db)):
    """Get all responses for a debate."""
    return db.query(MPResponse).filter(MPResponse.debate_id == debate_id).all()
