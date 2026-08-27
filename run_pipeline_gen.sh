#!/bin/bash
set -e
echo "▶ STEP 1: Fetching data..."
node fetch_reddit_puppeteer_core.cjs || echo "⚠ Data fetch failed"
echo "▶ STEP 2: Generating content..."
python3 generate_all_content_gemini.py
echo "▶ STEP 3: Visuals..."
python3 generate_carousel_today.py
python3 generate_infographic_today.py
if [ -d "carousel-routine" ]; then
    cd carousel-routine
    node screenshot_all.js
    node compile_pdf.js
    cd ..
fi
if [ -f "cap_infographic_today.cjs" ]; then
    node cap_infographic_today.cjs || echo "⚠ Infographic build failed"
fi
echo "▶ STEP 4: Delivering to Slack..."
python3 send_to_slack.py
