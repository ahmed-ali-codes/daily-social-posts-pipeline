# 🏛️ System Architecture: Daily LinkedIn Posts Pipeline

This document outlines the high-level architecture, data flow, and module responsibilities of the autonomous content generation pipeline.

---

## 1. High-Level Architecture

The system is designed as a **Data-Driven Multi-Agent Pipeline**. It operates in five distinct phases:

1. **Data Acquisition:** Scraping algorithms pull raw signals from RSS feeds, APIs, and the Web.
2. **AI Content Engine:** Large Language Models (LLMs) parse the data, analyze it against configured brand guidelines (the "Skills" and "Doctrine"), and generate multi-format text outputs.
3. **Visual Asset Compilation:** The pipeline dynamically generates HTML interfaces from the text and uses Headless Browsers (Puppeteer) to snapshot them into high-resolution PNGs and PDFs.
4. **Slack Delivery:** The generated assets are pushed to an internal Slack channel for manual review or notification.
5. **Headless Scheduling:** A final automation layer logs into LinkedIn and schedules the posts autonomously over a multi-day span.

### Core Data Flow Diagram

```mermaid
graph TD
    %% Styling
    classDef source fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef process fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef output fill:#e8f5e9,stroke:#388e3c,stroke-width:2px;
    classDef storage fill:#fff3e0,stroke:#f57c00,stroke-width:2px;

    %% Nodes
    A1[Reddit RSS/APIs] ::: source
    A2[AI News RSS] ::: source
    A3[Performance Logs] ::: storage
    
    B1[fetch_reddit_*.py] ::: process
    B2[fetch_ai_news_rss.py] ::: process
    
    C1[(reddit_data.json)] ::: storage
    C2[(ai_news_data.json)] ::: storage
    
    D1[LLM Generation Engine\nwrite_today_data.py / generate_all_content_gemini.py] ::: process
    
    E1[Brand Config\nbrand_config.json] ::: storage
    E2[Markdown Skills/Prompts] ::: storage
    
    F1[linkedin_posts_today.txt] ::: output
    F2[carousel_data.json] ::: storage
    F3[infographic_data.json] ::: storage
    
    G1[Puppeteer Renderers\nHTML -> PNG -> PDF] ::: process
    
    H1[Visual Assets\n.png, .pdf] ::: output
    
    I1[Slack Delivery\nsend_to_slack.py] ::: process
    I2[LinkedIn Scheduler\nnode schedule_all_posts.cjs] ::: process

    %% Edges
    A1 --> B1
    A2 --> B2
    B1 --> C1
    B2 --> C2
    
    C1 --> D1
    C2 --> D1
    A3 --> D1
    E1 --> D1
    E2 --> D1
    
    D1 --> F1
    D1 --> F2
    D1 --> F3
    
    F2 --> G1
    F3 --> G1
    G1 --> H1
    
    F1 --> I1
    H1 --> I1
    
    F1 --> I2
    H1 --> I2
```

---

## 2. Directory & Module Structure

The codebase is organized by functional domain to ensure clean separation of concerns.

### ⚙️ Orchestration (`*.py`, `*.sh`)
The master entry points that string the phases together.
- `run_pipeline.sh`: The master bash script that executes the end-to-end pipeline.
- `setup_brand.py`: The initialization script that personalizes the generic pipeline templates with user-specific configurations.

### 📡 Data Fetchers (`fetch_*.py`, `fetch_*.cjs`)
Scripts responsible for acquiring external signals.
- Support multiple fallback mechanisms (Apify → JSON endpoint → RSS).
- Designed to write normalized JSON arrays to local disk (`*_data.json`) to decouple fetching from generation.

### 🧠 LLM Content Engines (`generate_*.py`, `write_today_data.py`)
The intelligent core of the system.
- Reads `brand_config.json` and injects the parameters into the Markdown prompt files (`skills/`).
- Interfaces with Gemini/OpenRouter/Anthropic to generate structured text.
- Implements fallback logic if primary LLMs fail or rate-limit.
- Outputs a single consolidated text file (`linkedin_posts_today.txt`) and extracts visual data into JSON (`carousel_data.json`).

### 🎨 Visual Asset Builders (`carousel-routine/`)
The rendering engine.
- Takes the LLM-generated JSON layout data and maps it into static HTML templates.
- Runs `puppeteer-core` to launch headless Chrome browsers, rendering the HTML perfectly.
- Takes high-fidelity screenshots, cropping and saving them as `.png` files.
- Uses `pdf-lib` to stitch multiple slide PNGs into a seamless LinkedIn Carousel PDF.

### 📅 Schedulers (`schedule_*.cjs`)
The distribution layer.
- Uses `agent-browser` and Puppeteer to manage authenticated LinkedIn sessions.
- Automates the DOM manipulation required to upload PDFs, attach images, paste text, and hit the "Schedule for Later" buttons.
- Implements complex wait logic to handle LinkedIn's dynamic UI loading states.

---

## 3. Brand Injection Pattern

To maintain a generic, open-source-friendly repository, all brand-specific logic is abstracted. 

1. **Placeholder Strategy:** The codebase relies on placeholders (e.g., `{{BRAND_NAME}}`, `{{AUTHOR_NAME}}`) inside prompts and scripts.
2. **Hydration at Setup:** When a user runs `setup_brand.py`, it hydrates these placeholders permanently across the repository.
3. **Runtime Config:** At runtime, the Python generators also load `brand_config.json` to ensure any dynamically generated API payloads match the current brand identity.

---

## 4. Scalability & Maintenance

- **Adding New Channels:** To add Twitter/X support, you only need to create a new `schedule_twitter.cjs` script and append a new post format requirement to the system prompt in the generator scripts.
- **Modifying Visuals:** Visuals are entirely HTML/CSS based. To redesign the carousels or infographics, simply edit the HTML files in `carousel-routine/`. No Python or complex canvas drawing logic is required.
