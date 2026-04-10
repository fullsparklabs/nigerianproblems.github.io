#!/usr/bin/env python3
"""
Generate Jekyll blog posts from scraped Nigerian problems data
Uses Ollama AI to analyze, categorize, and summarize content
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from slugify import slugify
from ollama import chat

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PostGenerator:
    """Generate Jekyll blog posts from scraped data using AI"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / '_data'
        self.problems_dir = Path(__file__).parent.parent / '_problems'
        self.problems_dir.mkdir(exist_ok=True)
        self.model = os.environ.get('OLLAMA_MODEL', 'qwen2.5:latest')
        
    def load_articles(self) -> List[Dict]:
        """Load scraped articles"""
        articles_file = self.data_dir / 'scraped_articles.json'
        if not articles_file.exists():
            logger.warning("No scraped articles found. Run scraper.py first.")
            return []
        
        with open(articles_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def analyze_with_ai(self, article: Dict) -> Dict:
        """Use Ollama AI to analyze and enhance article"""
        try:
            prompt = f"""
You are an expert analyst of Nigerian history and current affairs. Analyze this article about a Nigerian problem and provide structured output.

ARTICLE:
Title: {article.get('title', '')}
Content: {article.get('content', '')[:3000]}

Provide your analysis in this exact JSON format:
{{
    "summary": "A concise 2-3 sentence summary of the problem",
    "categories": ["category1", "category2"],
    "tags": ["tag1", "tag2"],
    "impact": "High/Medium/Low",
    "affected_regions": ["region1", "region2"],
    "decade": "1960s/1970s/1980s/1990s/2000s/2010s/2020s",
    "problem_type": "Political/Economic/Social/Security/Infrastructure/Environmental/Health/Educational",
    "key_points": ["point1", "point2", "point3"]
}}

Categories should be from: political, economic, social, security, infrastructure, environmental, health, educational, governance, human_rights
Keep it concise and factual.
"""
            
            response = chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.3}
            )
            
            # Parse JSON from response
            content = response['message']['content']
            # Find JSON in response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                analysis = json.loads(content[start:end])
                return analysis
            else:
                logger.warning(f"Could not parse AI response for: {article.get('title', '')}")
                return self._default_analysis()
                
        except Exception as e:
            logger.error(f"Error analyzing with AI: {e}")
            return self._default_analysis()
    
    def _default_analysis(self) -> Dict:
        """Return default analysis if AI fails"""
        return {
            'summary': 'A documented problem affecting Nigeria.',
            'categories': ['general'],
            'tags': ['nigeria', 'problem'],
            'impact': 'Medium',
            'affected_regions': ['Nigeria'],
            'decade': '2020s',
            'problem_type': 'Social',
            'key_points': ['Details documented in sources']
        }
    
    def generate_frontmatter(self, article: Dict, analysis: Dict) -> str:
        """Generate Jekyll frontmatter"""
        # Parse date
        date_str = article.get('date', datetime.now().isoformat())
        try:
            # Try to parse various date formats
            if len(date_str) == 4 and date_str.isdigit():
                date = datetime(int(date_str), 1, 1)
            else:
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            date = datetime.now()
        
        categories = analysis.get('categories', ['general'])
        tags = analysis.get('tags', ['nigeria'])
        
        frontmatter = f"""---
title: "{article.get('title', 'Untitled').replace('"', '\\"')}"
date: {date.strftime('%Y-%m-%d %H:%M:%S')}
categories: [{', '.join(categories)}]
tags: [{', '.join(tags)}]
source: "{article.get('url', '')}"
source_name: "{article.get('source', 'Unknown')}"
impact: "{analysis.get('impact', 'Medium')}"
problem_type: "{analysis.get('problem_type', 'General')}"
affected_regions: [{', '.join(analysis.get('affected_regions', ['Nigeria']))}]
ai_generated: true
---
"""
        return frontmatter
    
    def generate_content(self, article: Dict, analysis: Dict) -> str:
        """Generate the blog post content"""
        summary = analysis.get('summary', 'No summary available.')
        key_points = analysis.get('key_points', [])
        
        content = f"\n## Summary\n\n{summary}\n\n"
        
        if key_points:
            content += "## Key Points\n\n"
            for point in key_points:
                content += f"- {point}\n"
            content += "\n"
        
        # Add original content if available
        original_content = article.get('content', '')
        if original_content and len(original_content) > 100:
            content += "## Details\n\n"
            # Limit content length
            content += original_content[:2000]
            if len(original_content) > 2000:
                content += "...\n\n*Content truncated for readability.*\n"
            content += "\n"
        
        content += f"\n*Source: [{article.get('source', 'Unknown')}]({article.get('url', '')})*\n"
        content += f"\n*This post was processed and categorized using AI analysis.*\n"
        
        return content
    
    def create_post(self, article: Dict, analysis: Dict):
        """Create a single blog post file"""
        # Generate filename
        date_str = article.get('date', datetime.now().isoformat())
        try:
            if len(date_str) == 4 and date_str.isdigit():
                date = datetime(int(date_str), 1, 1)
            else:
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            date = datetime.now()
        
        title = article.get('title', 'untitled')
        slug = slugify(title)
        filename = f"{date.strftime('%Y-%m-%d')}-{slug}.md"
        filepath = self.problems_dir / filename
        
        # Check if file already exists
        if filepath.exists():
            logger.info(f"Post already exists: {filename}, skipping")
            return
        
        # Generate content
        frontmatter = self.generate_frontmatter(article, analysis)
        content = self.generate_content(article, analysis)
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
            f.write(content)
        
        logger.info(f"Created post: {filename}")
    
    def run(self):
        """Generate all posts"""
        logger.info("Starting post generation...")
        
        # Load articles
        articles = self.load_articles()
        if not articles:
            logger.warning("No articles to process")
            return
        
        logger.info(f"Processing {len(articles)} articles...")
        
        # Process each article
        for i, article in enumerate(articles):
            try:
                logger.info(f"Processing article {i+1}/{len(articles)}: {article.get('title', '')[:50]}...")
                
                # Analyze with AI
                analysis = self.analyze_with_ai(article)
                
                # Create post
                self.create_post(article, analysis)
                
            except Exception as e:
                logger.error(f"Error processing article: {e}")
                continue
        
        logger.info("Post generation complete!")


if __name__ == '__main__':
    generator = PostGenerator()
    generator.run()
