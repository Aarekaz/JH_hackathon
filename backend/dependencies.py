from services.arxiv_service import ArxivService
from services.openai_service import OpenAIService
from functools import lru_cache
import os

@lru_cache()
def get_arxiv_service() -> ArxivService:
    return ArxivService()

@lru_cache()
def get_openai_service() -> OpenAIService:
    api_key = os.getenv("OPENAI_API_KEY")
    print("API KEY: ", api_key)
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return OpenAIService(api_key=api_key)
