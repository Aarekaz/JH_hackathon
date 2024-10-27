import logging
import os
from dotenv import load_dotenv
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.init_db import init_database
from routers import debates, moderator, policy_papers

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the app
app = FastAPI(title="AI Parliament API")

# Initialize database
init_database()

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
app.include_router(policy_papers.router)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now()}

# Add other endpoints and configurations as needed
