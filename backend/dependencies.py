from functools import lru_cache
from services.openai_service import OpenAIService
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@lru_cache()
def get_openai_service() -> OpenAIService:
    """Get or create OpenAI service instance."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return OpenAIService(api_key=api_key)

