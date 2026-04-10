#!/usr/bin/env python3
"""
Nigerian Problems Web Scraper
Scrapes Nigerian news and problems from various sources
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import feedparser
from ollama import chat

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ScrapedArticle:
    title: str
    url: str
    date: str
    source: str
    content: str
    summary: str = ""
    categories: List[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = []
        if self.tags is None:
            self.tags = []

class NigerianNewsScraper:
    """Scraper for Nigerian news and problems"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.articles: List[ScrapedArticle] = []
        self.output_dir = Path(__file__).parent.parent / '_data'
        self.output_dir.mkdir(exist_ok=True)
        
    def fetch_with_retry(self, url: str, retries: int = 3) -> Optional[requests.Response]:
        """Fetch URL with retry logic"""
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                return response
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                time.sleep(2 ** attempt)
        return None
    
    def scrape_news_sites(self) -> List[ScrapedArticle]:
        """Scrape from major Nigerian news sites"""
        news_sources = [
            {
                'name': 'Premium Times',
                'url': 'https://www.premiumtimesng.com/feed',
                'type': 'rss'
            },
            {
                'name': 'Vanguard Nigeria',
                'url': 'https://www.vanguardngr.com/feed/',
                'type': 'rss'
            },
            {
                'name': 'The Guardian Nigeria',
                'url': 'https://guardian.ng/feed/',
                'type': 'rss'
            },
            {
                'name': 'Punch Newspapers',
                'url': 'https://punchng.com/feed/',
                'type': 'rss'
            },
            {
                'name': 'Premium Times',
                'url': 'https://www.premiumtimesng.com/news',
                'type': 'web'
            },
        ]
        
        articles = []
        for source in news_sources:
            try:
                if source['type'] == 'rss':
                    articles.extend(self._scrape_rss(source))
                elif source['type'] == 'web':
                    articles.extend(self._scrape_website(source))
                time.sleep(1)  # Be polite
            except Exception as e:
                logger.error(f"Error scraping {source['name']}: {e}")
        
        return articles
    
    def _scrape_rss(self, source: Dict) -> List[ScrapedArticle]:
        """Scrape from RSS feed"""
        articles = []
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries[:20]:  # Limit to 20 per source
                article = ScrapedArticle(
                    title=entry.get('title', ''),
                    url=entry.get('link', ''),
                    date=entry.get('published', datetime.now().isoformat()),
                    source=source['name'],
                    content=entry.get('summary', '') or entry.get('description', ''),
                    summary=''
                )
                articles.append(article)
        except Exception as e:
            logger.error(f"Error scraping RSS {source['name']}: {e}")
        
        return articles
    
    def _scrape_website(self, source: Dict) -> List[ScrapedArticle]:
        """Scrape from website"""
        articles = []
        response = self.fetch_with_retry(source['url'])
        if not response:
            return articles
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Extract article links
        for link in soup.find_all('a', href=True):
            href = link['href']
            if any(keyword in href.lower() for keyword in ['/news/', '/article/', '/story/']):
                title = link.get_text(strip=True)
                if title and len(title) > 20:
                    full_url = href if href.startswith('http') else f"https://www.premiumtimesng.com{href}"
                    article = ScrapedArticle(
                        title=title,
                        url=full_url,
                        date=datetime.now().isoformat(),
                        source=source['name'],
                        content='',
                        summary=''
                    )
                    articles.append(article)
        
        return articles[:10]  # Limit articles
    
    def scrape_historical_problems(self, year_range: str = 'all') -> List[ScrapedArticle]:
        """Search for historical Nigerian problems by year"""
        articles = []
        
        # Define search queries for different types of problems
        problem_categories = [
            "corruption scandal",
            "military coup",
            "economic crisis",
            "fuel scarcity",
            "unemployment",
            "infrastructure collapse",
            "security crisis",
            "healthcare crisis",
            "education strike",
            "ethnic conflict",
            "oil spill",
            "flooding disaster",
            "power crisis",
            "poverty",
            "human rights"
        ]
        
        if year_range == 'all':
            years = list(range(1960, 2025))
        else:
            try:
                start, end = map(int, year_range.split('-'))
                years = list(range(start, min(end + 1, 2025)))
            except:
                years = list(range(1960, 2025))
        
        # Sample years to avoid too many requests
        sample_years = years[::max(1, len(years) // 20)]  # Sample ~20 years
        
        for category in problem_categories[:5]:  # Limit categories for now
            for year in sample_years[:10]:  # Limit years per run
                try:
                    # Use Wikipedia and other archive sources
                    search_url = f"https://en.wikipedia.org/wiki/{year}_in_Nigeria"
                    response = self.fetch_with_retry(search_url)
                    if response:
                        soup = BeautifulSoup(response.content, 'lxml')
                        content = soup.get_text()[:2000]  # Limit content
                        
                        article = ScrapedArticle(
                            title=f"Nigeria {category.capitalize()} - {year}",
                            url=search_url,
                            date=f"{year}-01-01",
                            source="Wikipedia Archive",
                            content=content,
                            summary='',
                            categories=[category.replace(' ', '_')],
                            tags=[str(year), category, 'nigeria']
                        )
                        articles.append(article)
                
                except Exception as e:
                    logger.error(f"Error scraping historical data for {year}: {e}")
                
                time.sleep(0.5)
        
        return articles
    
    def scrape_specific_problem_sites(self) -> List[ScrapedArticle]:
        """Scrape from sites that document Nigerian problems"""
        articles = []
        
        sources = [
            {
                'name': 'Amnesty International Nigeria',
                'url': 'https://www.amnesty.org/en/location/africa/west-africa/nigeria/report-nigeria/',
                'categories': ['human_rights', 'governance']
            },
            {
                'name': 'Human Rights Watch Nigeria',
                'url': 'https://www.hrw.org/africa/nigeria',
                'categories': ['human_rights', 'conflict']
            },
            {
                'name': 'World Bank Nigeria',
                'url': 'https://www.worldbank.org/en/country/nigeria/overview',
                'categories': ['economy', 'development']
            },
        ]
        
        for source in sources:
            try:
                response = self.fetch_with_retry(source['url'])
                if response:
                    soup = BeautifulSoup(response.content, 'lxml')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    content = soup.get_text()
                    # Clean up whitespace
                    lines = (line.strip() for line in content.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    content = ' '.join(chunk for chunk in chunks if chunk)
                    
                    article = ScrapedArticle(
                        title=f"{source['name']} - Nigeria Report",
                        url=source['url'],
                        date=datetime.now().isoformat(),
                        source=source['name'],
                        content=content[:5000],  # Limit content
                        summary='',
                        categories=source['categories'],
                        tags=['nigeria', 'report'] + source['categories']
                    )
                    articles.append(article)
                
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error scraping {source['name']}: {e}")
        
        return articles
    
    def save_articles(self, articles: List[ScrapedArticle]):
        """Save articles to JSON file"""
        output_file = self.output_dir / 'scraped_articles.json'
        
        # Load existing articles
        existing_articles = []
        if output_file.exists():
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    existing_articles = json.load(f)
            except:
                existing_articles = []
        
        # Convert new articles to dicts
        new_articles = [asdict(a) for a in articles]
        
        # Merge and deduplicate
        all_articles = existing_articles + new_articles
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article.get('url') not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        # Save
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unique_articles, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(unique_articles)} articles to {output_file}")
    
    def run(self, year_range: str = 'all'):
        """Run all scrapers"""
        logger.info("Starting Nigerian Problems scraper...")
        
        # Scrape current news
        logger.info("Scraping news sites...")
        news_articles = self.scrape_news_sites()
        logger.info(f"Found {len(news_articles)} news articles")
        
        # Scrape historical problems
        logger.info(f"Scraping historical problems ({year_range})...")
        historical_articles = self.scrape_historical_problems(year_range)
        logger.info(f"Found {len(historical_articles)} historical articles")
        
        # Scrape problem documentation sites
        logger.info("Scraping problem documentation sites...")
        problem_articles = self.scrape_specific_problem_sites()
        logger.info(f"Found {len(problem_articles)} problem articles")
        
        # Combine all articles
        all_articles = news_articles + historical_articles + problem_articles
        
        # Save to file
        self.save_articles(all_articles)
        
        logger.info(f"Scraping complete! Total articles: {len(all_articles)}")
        return all_articles


if __name__ == '__main__':
    year_range = os.environ.get('YEAR_RANGE', 'all')
    scraper = NigerianNewsScraper()
    scraper.run(year_range)
