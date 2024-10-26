import asyncio
import xml.etree.ElementTree as ET
from typing import List, Optional, Dict
import httpx
from datetime import datetime, timezone
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Changed to DEBUG level
logger = logging.getLogger(__name__)

class ArxivService:
    """Service to interact with ArXiv API."""
    
    def __init__(self):
        """Initialize ArXiv service with base URL."""
        self.base_url = "http://export.arxiv.org/api/query"
        self.namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom',
            'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'
        }
        
    async def fetch_ai_papers(self, max_results: int = 10) -> List[Dict]:
        """
        Fetch recent AI papers from ArXiv API.
        
        Args:
            max_results: Maximum number of results to return (default: 10)
            
        Returns:
            List of papers with their metadata
        """
        try:
            # Simplified query
            params = {
                "search_query": "all:ai",
                "start": 0,
                "max_results": max_results
            }
            
            headers = {
                "User-Agent": "AI Parliament Simulator/1.0 (mailto:your@email.com)"
            }

            logger.debug(f"Making request to ArXiv API with URL: {self.base_url}")
            logger.debug(f"Parameters: {params}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params, headers=headers)
                response.raise_for_status()
                
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response content preview: {response.text[:500]}")

            # Parse XML
            root = ET.fromstring(response.text)
            entries = root.findall('.//atom:entry', self.namespaces)
            logger.info(f"Found {len(entries)} entries in XML")

            papers = []
            for i, entry in enumerate(entries, 1):
                try:
                    # Basic required fields
                    title_elem = entry.find('atom:title', self.namespaces)
                    summary_elem = entry.find('atom:summary', self.namespaces)
                    
                    if title_elem is None or summary_elem is None:
                        logger.warning(f"Entry {i} missing title or summary")
                        continue
                        
                    title = title_elem.text.strip()
                    summary = summary_elem.text.strip()
                    
                    logger.debug(f"Processing paper {i}: {title[:50]}...")

                    paper = {
                        'title': title,
                        'summary': summary,
                        'content': f"Title: {title}\n\nAbstract:\n{summary}",
                        'source': 'arxiv',
                        'url': '',
                        'status': 'pending'
                    }
                    
                    # Try to get PDF link
                    for link in entry.findall('atom:link', self.namespaces):
                        if link.get('title') == 'pdf':
                            paper['url'] = link.get('href', '')
                            break
                    
                    papers.append(paper)
                    logger.info(f"Successfully processed paper {i}: {title[:50]}")
                    
                except Exception as e:
                    logger.error(f"Error processing entry {i}: {str(e)}")
                    continue

            logger.info(f"Successfully processed {len(papers)} papers")
            return papers
            
        except Exception as e:
            logger.error(f"Error in fetch_ai_papers: {str(e)}")
            raise

    async def get_paper_by_id(self, arxiv_id: str) -> Optional[dict]:
        """Fetch a specific paper by ArXiv ID."""
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            # Changed from async to sync
            result = next(search.results(), None)
            
            if result:
                return {
                    'title': result.title,
                    'summary': result.summary,
                    'url': result.pdf_url,
                    'source': 'arxiv',
                    'content': f"{result.title}\n\n{result.summary}\n\nAuthors: {', '.join(a.name for a in result.authors)}"
                }
            return None
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching paper from ArXiv: {str(e)}"
            )
