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
        
    def fetch_with_retry(self, url: str, retries: int = 2) -> Optional[requests.Response]:
        """Fetch URL with retry logic"""
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=15)
                response.raise_for_status()
                return response
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                time.sleep(1)
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
                'name': 'Channels Television',
                'url': 'https://www.channelstv.com/feed/',
                'type': 'rss'
            },
            {
                'name': 'Sahara Reporters',
                'url': 'https://saharareporters.com/taxonomy/term/39/feed',
                'type': 'rss'
            },
        ]
        
        articles = []
        for source in news_sources:
            try:
                if source['type'] == 'rss':
                    articles.extend(self._scrape_rss(source))
                time.sleep(0.5)  # Be polite
            except Exception as e:
                logger.error(f"Error scraping {source['name']}: {e}")
        
        return articles
    
    def _scrape_rss(self, source: Dict) -> List[ScrapedArticle]:
        """Scrape from RSS feed"""
        articles = []
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries[:15]:  # Limit to 15 per source
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
    
    def scrape_historical_problems(self, year_range: str = 'all') -> List[ScrapedArticle]:
        """Search for historical Nigerian problems"""
        articles = []
        
        # Wikipedia pages that actually exist for Nigeria
        wiki_pages = [
            ('History of Nigeria', 'History_of_Nigeria'),
            ('Nigerian Civil War', 'Nigerian_Civil_War'),
            ('1966 Nigerian coup', '1966_Nigerian_coup_d%27%C3%A9tat'),
            ('1983 Nigerian coup', '1983_Nigerian_coup_d%27%C3%A9tat'),
            ('1993 Nigerian election', 'Nigerian_general_elections,_1993'),
            ('Abacha regime', 'Sani_Abacha'),
            ('Boko Haram insurgency', 'Boko_Haram_insurgency'),
            ('EndSARS protests', 'EndSARS'),
            ('Niger Delta conflict', 'Niger_Delta_conflict'),
            ('Fuel subsidy protests', '2012_Nigeria_fuel_subsidy_protests'),
            ('Chibok schoolgirls kidnapping', 'Chibok_schoolgirls_kidnapping'),
            ('Nigerian Civil War - Biafra', 'Republic_of_Biafra'),
            ('2020 EndSARS', '2020_EndSARS_protests'),
            ('Nigeria economic crisis', 'Economy_of_Nigeria'),
            ('Oil pollution in Niger Delta', 'Oil_pollution_in_the_Niger_Delta'),
        ]
        
        # Year-specific major events
        year_events = {
            '1960': [('Independence', 'Independence_Day_(Nigeria)')],
            '1963': [('Republic declared', 'First_Nigerian_Republic')],
            '1966': [('Military coups', '1966_Nigerian_coup_d%27%C3%A9tat'), ('Counter-coup', '1966_Nigerian_counter-coup')],
            '1967': [('Biafra declared', 'Republic_of_Biafra')],
            '1970': [('Civil War ends', 'Nigerian_Civil_War')],
            '1975': [('Coup against Gowon', '1975_Nigerian_coup_d%27%C3%A9tat')],
            '1979': [('Return to democracy', 'Second_Nigerian_Republic')],
            '1983': [('Coup against Shagari', '1983_Nigerian_coup_d%27%C3%A9tat')],
            '1993': [('June 12 annulment', 'Nigerian_general_elections,_1993')],
            '1999': [('Fourth Republic', 'Fourth_Nigerian_Republic')],
            '2009': [('Boko Haram begins', 'Boko_Haram_insurgency')],
            '2014': [('Chibok kidnapping', 'Chibok_schoolgirls_kidnapping')],
            '2015': [('APC victory', '2015_Nigerian_general_election')],
            '2020': [('EndSARS protests', '2020_EndSARS_protests')],
            '2023': [('General elections', '2023_Nigerian_general_election')],
        }
        
        # Scrape Wikipedia articles
        all_pages = wiki_pages.copy()
        
        # Add year-specific events
        for year, events in year_events.items():
            all_pages.extend([(f"{year}: {e[0]}", e[1]) for e in events])
        
        for title, wiki_slug in all_pages:
            try:
                url = f"https://en.wikipedia.org/wiki/{wiki_slug}"
                response = self.fetch_with_retry(url)
                if response:
                    soup = BeautifulSoup(response.content, 'lxml')
                    
                    # Get main content
                    content_div = soup.find('div', {'id': 'mw-content-text'})
                    if content_div:
                        paragraphs = content_div.find_all('p', limit=10)
                        content = '\n'.join([p.get_text() for p in paragraphs if p.get_text().strip()])
                        
                        if len(content) > 200:  # Only keep substantial articles
                            article = ScrapedArticle(
                                title=f"Nigeria: {title}",
                                url=url,
                                date=datetime.now().isoformat(),
                                source="Wikipedia",
                                content=content[:3000],
                                summary='',
                                categories=['historical'],
                                tags=['nigeria', title.lower().replace(' ', '_')]
                            )
                            articles.append(article)
                
                time.sleep(0.3)
            except Exception as e:
                logger.error(f"Error scraping {title}: {e}")
        
        return articles
    
    def scrape_problem_documentation_sites(self) -> List[ScrapedArticle]:
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
                'name': 'World Bank Nigeria Overview',
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
                        content=content[:5000],
                        summary='',
                        categories=source['categories'],
                        tags=['nigeria', 'report'] + source['categories']
                    )
                    articles.append(article)
                
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Error scraping {source['name']}: {e}")
        
        return articles
    
    def filter_problem_articles(self, articles: List[ScrapedArticle]) -> List[ScrapedArticle]:
        """Filter articles that are about problems/issues"""
        problem_keywords = [
            'crisis', 'problem', 'conflict', 'protest', 'scandal', 'corruption',
            'violence', 'attack', 'kill', 'death', 'unemployment', 'poverty',
            'infrastructure', 'power', 'electricity', 'fuel', 'subsidy',
            'strike', 'healthcare', 'education', 'insecurity', 'bandit',
            'kidnap', 'terrorism', 'boko haram', 'herdsmen', 'flooding',
            'erosion', 'pollution', 'oil spill', 'economic', 'recession',
            'inflation', 'currency', 'naira', 'debt', 'budget',
            'military', 'coup', 'civil war', 'biafra', 'end', 'sars',
            'police', 'brutality', 'human rights', 'abuse'
        ]
        
        filtered = []
        for article in articles:
            text = f"{article.title} {article.content}".lower()
            if any(keyword in text for keyword in problem_keywords):
                filtered.append(article)
        
        return filtered
    
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
            if article.get('url') not in seen_urls and article.get('url'):
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
        
        # Filter for problem-related news
        problem_news = self.filter_problem_articles(news_articles)
        logger.info(f"Filtered to {len(problem_news)} problem-related articles")
        
        # Scrape historical problems
        logger.info(f"Scraping historical problems...")
        historical_articles = self.scrape_historical_problems(year_range)
        logger.info(f"Found {len(historical_articles)} historical articles")
        
        # Scrape problem documentation sites
        logger.info("Scraping problem documentation sites...")
        problem_articles = self.scrape_problem_documentation_sites()
        logger.info(f"Found {len(problem_articles)} problem articles")
        
        # Combine all articles
        all_articles = problem_news + historical_articles + problem_articles
        
        # Save to file
        self.save_articles(all_articles)
        
        logger.info(f"Scraping complete! Total articles: {len(all_articles)}")
        return all_articles


if __name__ == '__main__':
    year_range = os.environ.get('YEAR_RANGE', 'all')
    scraper = NigerianNewsScraper()
    scraper.run(year_range)
