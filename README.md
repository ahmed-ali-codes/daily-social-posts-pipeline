# 🚀 Daily LinkedIn Posts Pipeline

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
> *Original concept by **The Solo Entrepreneur** | Enterprise Refactor & Engineering by **Ahmed Ali***
> 
> An autonomous content pipeline leveraging AI, Web Scraping, and Headless Browsers to build, design, and schedule a complete month of high-converting content for founders and agencies.

This pipeline is a completely generic and customizable template. You can set it up for your own brand, industry, and target audience, and it will run the exact same data-fetching and content-generation routines tailored to you.

📚 **Want to see how it works under the hood?** Read the [System Architecture Guide](ARCHITECTURE.md).

---

## Prerequisites

### Software
- **Node.js** ≥ 18 (for Puppeteer scripts and carousel rendering)
- **Python 3.10+** (for data fetching and LLM generation)
- **agent-browser** CLI (for LinkedIn scheduling via browser automation)
- **puppeteer-core** npm package (global or in `carousel-routine/`)

### API Keys (stored in `.env`)
Copy `.env.example` to `.env` and fill in your keys:
```
OPENROUTER_API_KEY=...      # For LLM post generation
ANTHROPIC_API_KEY=...       # Alternative LLM provider
SLACK_BOT_TOKEN=...         # For Slack delivery
SLACK_CHANNEL_ID=...        # Target Slack channel
SCRAPINGDOG_API_KEY=...     # Optional: for X/Twitter research
LINKEDIN_PERSONAL_URL=...   # URL to personal linkedin
LINKEDIN_COMPANY_URL=...    # URL to company page
INSTAGRAM_URL=...           # URL to instagram
```

### NPM Dependencies
```bash
cd carousel-routine && npm install
```

---

## 🚀 Setting Up Your Brand

This codebase uses placeholder tags. To personalize it for your brand:

1. Edit the `brand_config.json` file in the root directory with your details:
   ```json
   {
     "BRAND_NAME": "Your Company Name",
     "BRAND_SHORT_NAME": "YourCompany",
     "AUTHOR_NAME": "Your Name",
     "AUTHOR_TYPE": "{{AUTHOR_TYPE}}",
     "BRAND_DOMAIN": "Your industry/niche domain",
     "TARGET_AUDIENCE": "Your target audience",
     "POST_SCHEDULE_COMPANY": "schedule_company.cjs",
     "POST_SCHEDULE_PERSONAL": "schedule_personal.cjs"
   }
   ```
2. Run the initialization script:
   ```bash
   python3 setup_brand.py
   ```
   This will safely configure all internal scripts, prompts, and automation sequences to use your brand's specific details.

---

## Pipeline Overview

```
┌─────────────────────────────────────────────────────┐
│  PHASE 1: DATA FETCHING                              │
│  ├── Reddit: relevant subreddits via RSS/JSON/Apify  │
│  ├── AI News: industry sources                       │
│  └── Infographic dataset: 1 fresh dataset via search │
├─────────────────────────────────────────────────────┤
│  PHASE 2: CONTENT GENERATION (via LLM)               │
│  ├── Reddit posts: Collab Article, Poll, Carousel    │
│  ├── Industry News posts: 7 archetypes               │
│  └── Performance posts: report-driven winners        │
├─────────────────────────────────────────────────────┤
│  PHASE 3: VISUAL ASSET CREATION                      │
│  ├── Carousel: 7 slides → PNG → PDF                  │
│  └── Infographic: HTML → PNG screenshot              │
├─────────────────────────────────────────────────────┤
│  PHASE 4: SLACK DELIVERY                             │
│  ├── All post texts to Slack                         │
│  ├── Carousel PDF upload                             │
│  └── Infographic PNG upload                          │
├─────────────────────────────────────────────────────┤
│  PHASE 5: LINKEDIN SCHEDULING                        │
│  ├── Launch agent-browser with LinkedIn session      │
│  ├── Run schedule scripts                            │
│  └── Posts scheduled for the next 3 days             │
└─────────────────────────────────────────────────────┘
```

---

## How to Run (Step by Step)

### Phase 1: Fetch Data
```bash
# Try Apify first (most reliable, requires API key)
python3 fetch_reddit_apify.py

# If Apify fails, try JSON endpoints
python3 fetch_reddit_fallback.py
```

### Phase 2: Generate Content
The content generation is handled by the AI agent reading your personalized `.md` skill files:
```bash
python3 write_today_data.py
```
Output: `company_linkedin_posts_YYYYMMDD.txt`

### Phase 3: Build Visual Assets

**Carousel:**
```bash
cd carousel-routine && node screenshot_all.js
node compile_pdf.js
```

**Infographic:**
```bash
node cap_infographic_today.cjs
```

### Phase 4: Send to Slack
```bash
python3 send_to_slack.py
```

### Phase 5: Schedule on LinkedIn
```bash
# 1. Launch browser with LinkedIn session
agent-browser --session-name linkedin_bot open https://www.linkedin.com/feed/

# 2. Run the scheduling script
node schedule_all_posts.cjs
```

---

## Deduplication Rules

- **Carousel hooks**: The system reads `carousel-hook-log.json` before picking a style. Last used style is banned. 
- **Infographic topics**: The system reads `infographic-run-log.json` to never repeat a topic from the last 30 days.
- **Post topics**: No two posts in the same batch will cover the same source material.
