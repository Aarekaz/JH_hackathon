import asyncio
import logging
from services.arxiv_service import ArxivService

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_arxiv_service():
    service = ArxivService()
    try:
        papers = await service.fetch_ai_papers(max_results=3)
        logger.info(f"Retrieved {len(papers)} papers")
        
        for i, paper in enumerate(papers, 1):
            logger.info(f"\nPaper {i}:")
            logger.info(f"Title: {paper['title']}")
            logger.info(f"Summary: {paper['summary'][:200]}...")
            logger.info(f"URL: {paper['url']}")
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_arxiv_service())

