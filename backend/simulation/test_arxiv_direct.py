import asyncio
import logging
import xml.etree.ElementTree as ET

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_arxiv_api():
    """Test ArXiv API directly."""
    try:
        base_url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": "cat:cs.AI",
            "start": 0,
            "max_results": 3
        }
        headers = {
            "User-Agent": "AI Parliament Simulator/1.0"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info("Making request to ArXiv API...")
            response = await client.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response content: {response.text[:1000]}...")  # First 1000 chars
            
            # Parse XML
            root = ET.fromstring(response.text)
            
            # Define namespaces
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            # Find all entries
            entries = root.findall('.//atom:entry', namespaces)
            logger.info(f"Found {len(entries)} entries")
            
            # Print each entry's title
            for entry in entries:
                title = entry.find('atom:title', namespaces)
                if title is not None:
                    logger.info(f"Title: {title.text}")
        
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_arxiv_api())

