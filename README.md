# Nigerian Problems Archive

A comprehensive, AI-powered archive documenting problems Nigeria has faced from independence (1960) to present day.

**Live Site**: [nigerianproblems.github.io](https://nigerianproblems.github.io)

## 🇳🇬 What is This?

This project automatically scrapes, analyzes, and archives Nigerian news and problems using:
- **Web Scraping**: Collects news from major Nigerian sources and historical archives
- **AI Analysis**: Uses Ollama (Qwen model) to categorize, summarize, and tag content
- **Jekyll Blog**: Presents the archive in a clean, searchable format
- **GitHub Actions**: Runs the entire pipeline automatically on a schedule

## 📚 What's Documented

- Political instability and military coups
- Economic challenges and recessions
- Security issues and conflicts (Boko Haram, banditry, etc.)
- Infrastructure deficits (power, roads, water)
- Public health crises (Ebola, COVID-19, etc.)
- Educational challenges (ASUU strikes, infrastructure)
- Environmental problems (oil spills, flooding, desertification)
- Corruption and governance issues
- Social and ethnic tensions
- Human rights issues

## 🚀 Quick Start

### Deploy to GitHub Pages

1. **Fork/Clone this repository**
   ```bash
   git clone https://github.com/nigerianproblems/nigerianproblems.github.io.git
   cd nigerianproblems.github.io
   ```

2. **Enable GitHub Pages**
   - Go to repository Settings → Pages
   - Set source to "GitHub Actions"
   - The site will be available at `https://yourusername.github.io`

3. **First Manual Run**
   - Go to Actions tab
   - Click "Scrape and Update Nigerian Problems"
   - Click "Run workflow"
   - Optionally specify a year range (e.g., `1960-1970`, `2020-2024`, or `all`)

4. **Wait for Build**
   - The workflow will scrape, analyze, and generate posts
   - Site will be deployed automatically

## 🤖 How It Works

### Architecture

```
┌─────────────────┐
│  GitHub Actions │ (Every 6 hours or manual)
└────────┬────────┘
         │
    ┌────▼────┐
    │ Scraper │ (Python - scraper.py)
    │         │ - News RSS feeds
    │         │ - Historical archives
    │         │ - Problem documentation sites
    └────┬────┘
         │
    ┌────▼──────────────┐
    │  Ollama AI (Qwen) │ (generate_posts.py)
    │                   │ - Categorize problems
    │                   │ - Generate summaries
    │                   │ - Extract key points
    │                   │ - Tag and organize
    └────┬──────────────┘
         │
    ┌────▼─────┐
    │  Jekyll  │ (Build static site)
    │  Blog    │ - Generate HTML
    │          │ - Apply theme
    └────┬─────┘
         │
    ┌────▼──────────┐
    │ GitHub Pages  │ (Deploy)
    └───────────────┘
```

### Automated Workflow

The GitHub Actions workflow (`.github/workflows/scrape.yml`):

1. Sets up Python and Ollama
2. Runs the web scraper (`scripts/scraper.py`)
3. Runs AI-powered post generation (`scripts/generate_posts.py`)
4. Commits new content to the repository
5. Builds and deploys the Jekyll site

### AI Analysis

Each article is processed by Ollama's Qwen model which:
- Generates a concise summary
- Categorizes the problem (political, economic, security, etc.)
- Extracts key points
- Determines impact level (High/Medium/Low)
- Identifies affected regions
- Tags with relevant keywords

## 🛠️ Local Development

### Prerequisites

- Python 3.11+
- Ruby 3.0+ (for Jekyll)
- Ollama (for AI analysis)

### Setup

1. **Install Ollama**
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Pull the model
   ollama pull qwen2.5:latest
   ```

2. **Install Python dependencies**
   ```bash
   cd scripts
   pip install -r requirements.txt
   ```

3. **Install Ruby dependencies**
   ```bash
   bundle install
   ```

4. **Run scraper locally**
   ```bash
   cd scripts
   python scraper.py
   ```

5. **Generate posts with AI**
   ```bash
   python generate_posts.py
   ```

6. **Preview the site**
   ```bash
   bundle exec jekyll serve
   ```

## 📁 Project Structure

```
├── _config.yml              # Jekyll configuration
├── _layouts/                # Page layouts
│   ├── default.html
│   └── problem.html
├── _problems/               # Generated blog posts (auto-created)
├── _data/                   # Scraped data (auto-created)
│   └── scraped_articles.json
├── assets/
│   └── css/
│       └── style.css        # Custom styling
├── scripts/
│   ├── scraper.py           # Web scraping script
│   ├── generate_posts.py    # AI-powered post generation
│   └── requirements.txt     # Python dependencies
├── .github/
│   └── workflows/
│       └── scrape.yml       # GitHub Actions workflow
├── index.html               # Home page
├── timeline.md              # Timeline view
├── about.md                 # About page
└── README.md                # This file
```

## ⚙️ Configuration

### Workflow Schedule

By default, the scraper runs every 6 hours. To change this, edit `.github/workflows/scrape.yml`:

```yaml
on:
  schedule:
    # Run every 6 hours
    - cron: '0 */6 * * *'
```

### Ollama Model

The default model is `qwen2.5:latest`. To use a different model:

1. Pull the model in Ollama: `ollama pull llama3.2`
2. Update the environment variable in the workflow:
   ```yaml
   env:
     OLLAMA_MODEL: llama3.2:latest
   ```

### Scraping Sources

Add more sources in `scripts/scraper.py`:

```python
news_sources = [
    {
        'name': 'Your News Source',
        'url': 'https://example.com/feed',
        'type': 'rss'  # or 'web'
    },
]
```

## 📊 Categories

Problems are automatically categorized into:

- **political**: Government, elections, coups, policy issues
- **economic**: Recessions, inflation, unemployment, currency issues
- **security**: Conflicts, terrorism, banditry, kidnappings
- **infrastructure**: Power, roads, water, housing deficits
- **environmental**: Oil spills, flooding, desertification, erosion
- **health**: Disease outbreaks, healthcare access, hospital conditions
- **educational**: ASUU strikes, infrastructure, access issues
- **social**: Ethnic tensions, religious conflicts, poverty
- **governance**: Corruption, accountability, institutional issues
- **human_rights**: Abuses, freedom of speech, civil liberties

## 🔧 Troubleshooting

### Workflow fails

1. Check the Actions tab for error logs
2. Ensure Ollama starts properly (may take 30-60 seconds)
3. Check if rate limits are hit (add delays in scraper)

### No posts generated

1. Verify scraper found articles: Check `_data/scraped_articles.json`
2. Check AI model is running: `curl http://localhost:11434/api/tags`
3. Review logs in workflow output

### Site not deploying

1. Ensure `_config.yml` is valid YAML
2. Check for Ruby/Jekyll version compatibility
3. Review GitHub Pages deployment logs

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

- Add more news sources to the scraper
- Improve AI prompts for better analysis
- Enhance the Jekyll theme
- Add more historical data sources
- Improve categorization logic

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Test locally (see Local Development section)
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- News sources: Premium Times, Vanguard, The Guardian Nigeria, Punch Newspapers
- Historical data: Wikipedia, Amnesty International, Human Rights Watch, World Bank
- AI Analysis: Ollama and the Qwen model
- Hosting: GitHub Pages

## 📞 Contact

- Repository Issues: [Create an issue](https://github.com/nigerianproblems/nigerianproblems.github.io/issues)
- Twitter: [@nigerianproblems](https://twitter.com/nigerianproblems)

---

**Note**: This is an automated archive. All content is sourced from publicly available information and processed using AI. While we strive for accuracy, please verify important information from original sources.
