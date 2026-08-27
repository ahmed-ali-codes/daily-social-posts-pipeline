#!/bin/bash
# ==============================================================================
# 🚀 DAILY CONTENT PIPELINE — MASTER RUN SCRIPT
# Engineered by {{AUTHOR_NAME}}.
#
# Runs the entire autonomous content engine across 3 channels for {{AUTHOR_NAME}} & {{BRAND_SHORT_NAME}}.
# ==============================================================================

set -e

echo "=============================================================================="
echo "🚀 STARTING DAILY CONTENT PIPELINE"
echo "=============================================================================="

# 1. Fetch Reddit + AI News (Fail-safe chain)
echo ""
echo "▶ STEP 1: Fetching data..."
node fetch_reddit_puppeteer_core.cjs || echo "⚠ Data fetch failed, continuing with built-in contexts..."

# 2. Generate All Content (LLM Fallback Chain)
echo ""
echo "▶ STEP 2: Generating content (10 posts, 3 channels)..."
python3 generate_all_content_gemini.py

# 3. Build Visual Assets
echo ""
echo "▶ STEP 3: Building visual assets..."

echo "  Generating carousel HTML from today's data..."
python3 generate_carousel_today.py

echo "  Generating infographic HTML from today's data..."
python3 generate_infographic_today.py

echo "  Building Carousels..."
if [ -d "carousel-routine" ]; then
    cd carousel-routine
    node screenshot_all.js
    node compile_pdf.js
    cd ..
else
    echo "  ⚠ carousel-routine directory not found. Skipping carousels."
fi

echo "  Building Infographic..."
if [ -f "cap_infographic_today.cjs" ]; then
    node cap_infographic_today.cjs || echo "  ⚠ Infographic build failed. Continuing..."
else
    echo "  ⚠ cap_infographic_today.cjs not found. Skipping infographic."
fi

# 4. Send to Slack
echo ""
echo "▶ STEP 4: Delivering to Slack..."
python3 send_to_slack.py

# 5. Schedule LinkedIn Posts
echo ""
echo "▶ STEP 5: Scheduling LinkedIn Posts (with auto-login)..."
node schedule_all_with_login.cjs

echo ""
echo "=============================================================================="
echo "✅ PIPELINE RUN COMPLETE."
echo "   All 7 LinkedIn posts scheduled."
echo "   All 3 Instagram posts delivered to Slack for manual posting."
echo "=============================================================================="
