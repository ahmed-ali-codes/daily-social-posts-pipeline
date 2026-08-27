#!/usr/bin/env python3
"""
Daily Content Pipeline — Multi-Channel Generator
================================================
Generates 10 posts across 3 channels:
  - {{AUTHOR_NAME}} Personal LinkedIn   (4 posts: 9AM, 12PM, 3PM, 6PM IST)
  - {{BRAND_SHORT_NAME}} LinkedIn Page  (3 posts: 9AM, 12PM, 3PM IST)
  - {{BRAND_SHORT_NAME}} Instagram      (3 posts: Slack-delivered for manual posting)

LLM Fallback Chain:
  1. OpenRouter → google/gemma-4-31b-it:free
  2. OpenRouter → nvidia/nemotron-nano-9b-v2:free
  3. OpenRouter → qwen/qwen3-8b:free
  4. Gemini API direct (GEMINI_API_KEY)

Run: python3 generate_all_content_gemini.py [--date YYYY-MM-DD]
"""

import json
import logging
from llm_client import LLMClient
import urllib.request
import urllib.parse
import ssl
import sys
import os
import datetime
import time
import traceback

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# ============================================================
# ENV LOADING
# ============================================================
env_vars = {}
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, val = line.split("=", 1)
                env_vars[key.strip()] = val.strip()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

openrouter_key = env_vars.get("OPENROUTER_API_KEY", "")
gemini_key = env_vars.get("GEMINI_API_KEY", "")

if not openrouter_key and not gemini_key:
    logger.info("ERROR: No LLM API keys found in .env")
    sys.exit(1)

llm_client = LLMClient(openrouter_key, gemini_key)

# ============================================================
# DATE CONFIGURATION
# ============================================================
today = datetime.date.today()
if "--date" in sys.argv:
    try:
        today = datetime.date.fromisoformat(sys.argv[sys.argv.index("--date") + 1])
    except Exception:
        pass

schedule_date = today + datetime.timedelta(days=1)   # Schedule for TOMORROW by default
date_str = today.isoformat()
date_compact = date_str.replace("-", "")
sched_str = schedule_date.strftime("%m/%d/%Y")        # LinkedIn format: MM/DD/YYYY
day_seed = today.toordinal()

logger.info(f"\n{'='*60}")
logger.info(f"DAILY CONTENT PIPELINE — {date_str}")
logger.info(f"Scheduling posts for: {sched_str}")
logger.info(f"{'='*60}\n")

# ============================================================
# BRAND CONTEXT
# ============================================================
AHMED_BIO = """{{AUTHOR_NAME}} — Personal LinkedIn Brand
- Software engineering student (final year) at Curtin University Dubai
- Founder & CEO of {{BRAND_NAME}}, a Dubai-based AI automation agency
- UAE-based builder and AI automation specialist
- 1st place winner at EngageX Generative AI Hackathon
- Creator of MiniOS: an x86 operating system kernel written in C and Assembly
- n8n automation expert — builds WhatsApp bots, CRM systems, AI sales workflows for UAE businesses
- PHP, Python, JavaScript, x86 Assembly developer
- Builds in public. Shares real lessons from real projects."""

ECOTRUSTIA_BIO = """{{BRAND_NAME}} — Dubai-Based Digital Agency
Services:
- AI Automated Call Service (voice agents, 24/7 availability)
- WhatsApp Automation (instant replies, lead routing, workflow integration)
- AI Email Automation (intelligent response, continuous learning)
- AI Chatbots (24/7 support, business integration)
- AI Marketing Automation (campaign scheduling, multi-platform posting)
- Lead Generation & Targeting (data-driven, high-precision segmenting)
- AI Sales Agent (autonomous lead conversion, 24/7)
- Web Development (business sites, high-performance interfaces)
- SEO Optimization (organic traffic, search rankings)
- E-Commerce Solutions (Shopify, mobile optimization, checkout flows)
- Social Media Marketing (Facebook, Instagram, LinkedIn management)
Target market: ambitious generalists, Dubai founders, GCC regional businesses
Website: {{BRAND_SHORT_NAME_LOWER}}-solutions.vercel.app
Email: {{BRAND_SHORT_NAME_LOWER}}solutions@gmail.com
Phone: +971 55 788 8645
LinkedIn: linkedin.com/company/{{BRAND_SHORT_NAME_LOWER}}-solutions
Instagram: @{{BRAND_SHORT_NAME_LOWER}}"""

# ============================================================
# TOPIC ROTATION (date-seeded, deterministic)
# ============================================================
AHMED_STORY_TOPICS = [
    "Building MiniOS: writing an x86 kernel from scratch in C and Assembly while balancing university deadlines at Curtin Dubai",
    "How I won the EngageX Generative AI Hackathon by building a practical business tool instead of chasing novelty",
    "What 6 months of building n8n automation workflows for UAE clients taught me about real-world AI deployment",
    "The moment I realized UAE businesses need fundamentals fixed before AI automation will work for them",
    "Building a WhatsApp bot system for a Dubai retail client: what broke, what worked, what I'd do differently",
    "Running a real business while finishing a Computer Science degree: what people don't tell you about student founders",
    "Why most AI automation projects for ambitious generalists fail at the handoff stage (and how I learned to fix it)",
]

ECO_SERVICES = [
    "WhatsApp Automation",
    "AI Chatbots",
    "AI Email Automation",
    "AI Automated Call Service",
    "AI Sales Agent",
    "Lead Generation & Targeting",
    "Web Development",
    "SEO Optimization",
    "E-Commerce Solutions",
    "AI Marketing Automation",
]

ECO_IG_VISUAL_TOPICS = [
    {"topic": "AI automation stat for UAE businesses", "stat": "UAE businesses that automate lead follow-up respond 5x faster than those that don't"},
    {"topic": "WhatsApp bot benefit", "stat": "67% of customers prefer messaging a business on WhatsApp over calling"},
    {"topic": "AI sales agent benefit", "stat": "AI sales agents work 24/7 and never miss a lead — even at 2AM"},
    {"topic": "Dubai digital transformation", "stat": "Dubai's Vision 2031 targets 90% of government services to be AI-powered"},
    {"topic": "SEO for UAE businesses", "stat": "Businesses that blog 11+ times a month get 3x more traffic"},
    {"topic": "Email automation ROI", "stat": "For every AED 1 spent on email automation, businesses earn back AED 42"},
    {"topic": "Chatbot conversion fact", "stat": "Chatbots handle up to 80% of routine customer questions without human help"},
]

selected_story = AHMED_STORY_TOPICS[day_seed % len(AHMED_STORY_TOPICS)]
selected_service = ECO_SERVICES[day_seed % len(ECO_SERVICES)]
selected_ig_visual = ECO_IG_VISUAL_TOPICS[day_seed % len(ECO_IG_VISUAL_TOPICS)]
ahmed_hotake_topic = AHMED_STORY_TOPICS[(day_seed + 3) % len(AHMED_STORY_TOPICS)]

# ============================================================
# DATA LOADING (Reddit + AI News)
# ============================================================
reddit_posts = []
if os.path.exists("./reddit_data.json"):
    with open("./reddit_data.json") as f:
        reddit_posts = json.load(f)[:10]

ai_news = []
if os.path.exists("./ai_news_data.json"):
    with open("./ai_news_data.json") as f:
        ai_news = json.load(f)[:8]

reddit_summary = "\n".join([
    f"- [{p.get('subreddit','?')}] {p.get('title','')[:120]} (score: {p.get('score', 0)})"
    for p in reddit_posts[:5]
]) or "No Reddit data available. Use {{AUTHOR_NAME}}'s project experiences as source material."

news_summary = "\n".join([
    f"- {n.get('title','')[:120]} — {n.get('source','')}"
    for n in ai_news[:5]
]) or "No AI news data available. Use general AI industry knowledge for 2026."

# ============================================================
# LLM FALLBACK CHAIN
# ============================================================
OPENROUTER_MODELS = [
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "qwen/qwen3-8b:free",
    "meta-llama/llama-3.1-8b-instruct:free",
]

# ============================================================
# WRITING RULES (shared across prompts)
# ============================================================
AHMED_RULES = """
VOICE & RULES (CRITICAL — follow exactly):
- Casual-smart first-person voice. Young founder who doesn't gatekeep.
- NEVER start with "I" — start with an observation, action, or statement.
- No em-dashes. Use commas, semicolons, or periods instead.
- Hook on line 1. No preamble. Drop reader straight in.
- Short paragraphs: 2-3 lines max. Blank line between blocks.
- Max 3 hashtags, at the VERY END only.
- 200-400 words total.
- Ends with a question, reflection, or soft CTA ("DM me if you're working on something similar")
- BANNED WORDS: game-changer, delve, dive in, leverage (as verb), paradigm, synergy, holistic,
  cutting-edge, world-class, bespoke, groundbreaking, revolutionary, unlock, empower, transformative,
  disruptive, hustle, grind, thought leader, go viral, state-of-the-art, comprehensive, curated.
- BANNED PATTERNS: "No X. No Y. Just Z." / "It's not just about X..." / "Enter:" / "And here's the kicker"
- DO NOT include any title, label, or heading. Start directly with the hook.
"""

ECO_LI_RULES = """
VOICE & RULES (CRITICAL — follow exactly):
- Professional but not corporate. Confident Dubai agency voice.
- ALWAYS reference UAE/Dubai context: "UAE founders", "Dubai SMBs", "GCC market", "Vision 2031"
- Post structure: Pain point → Solution → Proof → CTA
- CTA must be one of: "Book a free audit", "DM us to get started", "Drop a comment below"
- No em-dashes. No "I". No first-person at all.
- 150-300 words total.
- BANNED WORDS: synergy, holistic, cutting-edge, world-class, bespoke, groundbreaking, revolutionary,
  game-changer, delve, empower, transformative, thought leader, disruptive.
- DO NOT include any title or label. Start directly with the opening line.
"""

ECO_IG_RULES = """
VOICE & RULES (CRITICAL — follow exactly):
- Punchy, visual-first, aspirational. UAE audience.
- Hook under 10 words (line 1).
- Body: 3-5 short punchy sentences. Each sentence on its own or same short paragraph.
- Max 5 emojis total.
- End with CTA + line break + 8-10 relevant hashtags.
- BANNED WORDS: game-changer, holistic, synergy, empower, revolutionary, cutting-edge, world-class.
- DO NOT include any title or label.
"""

# ============================================================
# GENERATE AHMED LINKEDIN POSTS (4 posts)
# ============================================================
print("\n" + "="*50)
logger.info("GENERATING AHMED PERSONAL LINKEDIN POSTS (4)")
print("="*50)

AHMED_SYS = f"You are {{AUTHOR_NAME}}'s LinkedIn ghostwriter.\n\n{AHMED_BIO}\n\n{AHMED_RULES}"
all_posts = {}

# POST 1 — Builder Story (9AM)
logger.info("\n[1/10] {{AUTHOR_NAME}} Post 1 — Builder Story (9:00 AM)...")
post1 = llm_client.call_llm(
    AHMED_SYS,
    f"""Write a LinkedIn text post for {{AUTHOR_NAME}}'s personal account.
Today's story topic: {selected_story}

Use specific details, real numbers, real feelings. Make it feel like {{AUTHOR_NAME}} is genuinely sharing a lesson from the trenches.
Reference his background naturally where relevant (Curtin Dubai, n8n, MiniOS, {{BRAND_SHORT_NAME}}).
Start directly with the hook. 200-400 words. Follow all voice rules exactly.
""",
    fallback_text="Building something real while studying is messy, and that's the point\n\nSix months ago I was writing x86 assembly at 2AM for MiniOS while my university deadline for systems programming was in 12 hours.\n\nMost people see this as a problem. I started seeing it as a feature.\n\nWhen you're forced to switch between theory and real implementation daily, your learning compresses. The kernel dev work made my Curtin assignments trivial. The assignments surfaced edge cases I'd missed in the kernel.\n\nThree things I noticed:\n- Real projects reveal gaps that textbooks don't show you\n- University deadlines force you to ship, which most side projects never do\n- The Dubai tech scene respects builders more than credentials at the early stage\n\nStill figuring out the balance. But I stopped trying to separate \"student mode\" from \"founder mode.\"\n\nThey're the same thing now.\n\nAre you building something while in school? What's the hardest part?\n\n#buildinpublic #studentfounder #dubaitech"
)
all_posts["ahmed_post_1"] = post1
time.sleep(2)

# POST 2 — AI/Tech Hot Take (12PM)
logger.info("\n[2/10] {{AUTHOR_NAME}} Post 2 — AI Hot Take (12:00 PM)...")
post2 = llm_client.call_llm(
    AHMED_SYS,
    f"""Write a LinkedIn text post for {{AUTHOR_NAME}}'s personal account.
Format: AI/Tech Hot Take from a UAE builder's perspective.
Topic inspiration (pick what's most relevant or combine): {ahmed_hotake_topic}

Current AI/tech news context:
{news_summary}

UAE builder angle: tie the AI trend back to what it means for builders and businesses in Dubai/UAE.
Start with a sharp, contrarian, or surprising observation.
200-350 words. Follow all voice rules exactly.
""",
    fallback_text="The biggest AI problem in UAE businesses isn't the technology\n\nIt's the data.\n\nI've built WhatsApp bots, email automations, and AI chatbots for a handful of Dubai SMBs over the past year. Every single time, the tech worked fine.\n\nThe problem was always the same: no clean data to feed it.\n\nUnsegmented contact lists. Leads in WhatsApp chat exports. Customer notes in someone's head. Product catalogs in Excel files from 2019.\n\nYou can't automate chaos. You have to organize first.\n\nBefore any UAE business owner asks me about AI, I now ask them three questions:\n- Can you export your customer list in 10 minutes?\n- Do you have a documented sales process, even a rough one?\n- Is your team actually going to use the system after I hand it over?\n\nIf the answer is no to any of these, the automation will fail. Not because the AI is bad. Because the foundation isn't there yet.\n\nMost agencies won't tell you this before selling you the package. I'd rather lose a client than build something that collects dust.\n\nAre UAE businesses ready for AI? Some are. Most need 3 months of cleanup first.\n\n#automation #uaetech #buildinpublic"
)
all_posts["ahmed_post_2"] = post2
time.sleep(2)

# POST 3 — Carousel Caption (3PM)
logger.info("\n[3/10] {{AUTHOR_NAME}} Post 3 — Carousel Caption (3:00 PM)...")
carousel_context = f"""
Story topic for this carousel: {selected_story}
Format: Step-by-step tutorial or breakdown from {{AUTHOR_NAME}}'s real experience.
Hook style: Before-After or numbered framework.
"""
post3_caption = llm_client.call_llm(
    AHMED_SYS,
    f"""Write the CAPTION ONLY for a LinkedIn carousel post for {{AUTHOR_NAME}}.
{carousel_context}
The caption should:
- Start with the hook (same hook as Slide 1)
- Tell what the carousel covers in 2-3 lines
- Ask an engagement question
- End with CTA to save/share
- Max 4 lines total
- Follow all voice rules
DO NOT write slide content, only the caption text.
""",
    fallback_text="Built an n8n workflow that saves 4 hours a week for a Dubai retail business\n\nHere's the exact 5-step setup I used (swipe to steal it).\n\nAre you still doing this manually in your business?\n\nSave this if you want to automate it.\n\n#automation #n8n #dubaitech"
)
all_posts["ahmed_post_3_caption"] = post3_caption
time.sleep(2)

# POST 4 — Engagement/Reflection (6PM)
logger.info("\n[4/10] {{AUTHOR_NAME}} Post 4 — Engagement/Reflection (6:00 PM)...")
post4 = llm_client.call_llm(
    AHMED_SYS,
    f"""Write a short LinkedIn engagement post for {{AUTHOR_NAME}}'s personal account.
Type: Reflection or question that sparks conversation.
Topic area: the contrast between what looks productive and what actually grows a business or skill.
Reference Dubai/UAE context naturally. 
100-200 words max. No list needed. Just a sharp reflection + a question at the end.
Follow all voice rules exactly.
""",
    fallback_text="The work that feels productive and the work that actually matters are usually different things\n\nSpent an hour last week reorganizing my n8n workflow folder structure. Made it look cleaner. Changed zero client outcomes.\n\nThe hour I spent sending 8 cold DMs to Dubai founders that same week resulted in 2 conversations and 1 proposal.\n\nWe hide behind setup work because it feels safe. No rejection. No awkward conversations. Just you and a tool that can't say no.\n\nReal growth usually feels uncomfortable.\n\nWhat's the \"cleanup task\" you're using to avoid the real work this week?\n\n#productivity #buildinpublic #founders"
)
all_posts["ahmed_post_4"] = post4
time.sleep(2)


# POST 5 (12AM)
logger.info("\n[11/18] {{AUTHOR_NAME}} Post 5 (12:00 AM)...")
ahmed_post_5 = llm_client.call_llm(AHMED_SYS, f"Write a short late-night reflection on building startups in Dubai. 100-200 words max. Reference: {news_summary}")
all_posts["ahmed_post_5"] = ahmed_post_5

# POST 6 (3AM)
logger.info("\n[12/18] {{AUTHOR_NAME}} Post 6 (3:00 AM)...")
ahmed_post_6 = llm_client.call_llm(AHMED_SYS, f"Write a data-driven post and an IMAGE BRIEF based on this AI news: {news_summary}. The image should visually represent the data/concept. Output format:\nIMAGE BRIEF:\n[detailed prompt for text-to-image model based on the data]\n\nCAPTION:\n[The post content]")
all_posts["ahmed_post_6"] = ahmed_post_6

# POST 7 (6AM)
logger.info("\n[13/18] {{AUTHOR_NAME}} Post 7 (6:00 AM)...")
ahmed_post_7 = llm_client.call_llm(AHMED_SYS, f"Write a short morning motivation post for founders. 100-200 words. Reference: {reddit_summary}")
all_posts["ahmed_post_7"] = ahmed_post_7

# POST 8 (9PM)
logger.info("\n[14/18] {{AUTHOR_NAME}} Post 8 (9:00 PM)...")
ahmed_post_8 = llm_client.call_llm(AHMED_SYS, f"Write a short post reviewing the day's progress in automation. 100-200 words.")
all_posts["ahmed_post_8"] = ahmed_post_8

# ============================================================
# GENERATE ECOTRUSTIA LINKEDIN POSTS (8 posts)
# ============================================================
print("\n" + "="*50)
logger.info("GENERATING ECOTRUSTIA LINKEDIN POSTS (3)")
print("="*50)

ECO_LI_SYS = f"You are {{BRAND_NAME}}' LinkedIn content writer.\n\n{ECOTRUSTIA_BIO}\n\n{ECO_LI_RULES}"

# POST 5 — Service Education + Infographic (9AM)
logger.info("\n[5/10] {{BRAND_SHORT_NAME}} LI Post 1 — Service Education (9:00 AM)...")
eco_post1 = llm_client.call_llm(
    ECO_LI_SYS,
    f"""Write a LinkedIn post for the {{BRAND_NAME}} company page.
Format: Service Education + Infographic companion text.
Service spotlight: {selected_service}

Structure: Pain point Dubai/UAE businesses face → How {selected_service} solves it → Specific result or benefit → CTA
Include at least one specific UAE/GCC reference.
150-300 words. Follow all agency voice rules exactly.
End with: "Book a free audit — link in bio"
""",
    fallback_text=f"Most Dubai businesses are losing leads because no one responds fast enough\n\nA prospect messages on WhatsApp at 11PM. Your team sees it at 9AM. By then, they've already found someone else.\n\nThis is the silent revenue killer for ambitious generalists.\n\n{selected_service} changes that. An AI-powered system that responds instantly, qualifies leads, and routes serious buyers to your sales team while you sleep.\n\nWe built one for a Dubai retail client last quarter. Response time went from 6 hours to under 90 seconds. Conversion rate on inbound WhatsApp leads went up by 34%.\n\nNo extra staff. No late nights. Just a system that runs 24/7 in the background.\n\nIf your business runs on customer conversations, you cannot afford 6-hour response gaps in 2026.\n\nBook a free audit — link in bio"
)
all_posts["eco_li_post_1"] = eco_post1

# Generate infographic brief
eco_infographic_brief = llm_client.call_llm(
    ECO_LI_SYS,
    f"""For the {{BRAND_SHORT_NAME}} LinkedIn service education post about {selected_service}, write an INFOGRAPHIC BRIEF only.
The brief describes what a data visualization image should look like.

Output format (fill in each field):
TITLE: [main headline for the infographic, max 8 words]
SUBTITLE: [1-line supporting text]
BADGE: [emoji + short category label, e.g. "📊 AI AUTOMATION STAT"]
KEY STAT: [the most striking number/stat to display large]
KEY STAT LABEL: [what the stat means in 6 words or less]
BAR STATS (3-5 items): [label | value%]
SOURCE: [Source: [research org or "{{BRAND_NAME}} Research"] | @{{BRAND_SHORT_NAME_LOWER}}]

Make the stats realistic and related to {selected_service} ROI for UAE/GCC businesses.
""",
    fallback_text=f"""TITLE: The UAE Business Automation Gap
SUBTITLE: Why {selected_service} is no longer optional for Dubai SMBs
BADGE: 📊 AUTOMATION ROI
KEY STAT: 5x
KEY STAT LABEL: Faster lead response with automation
BAR STATS:
- Businesses using automation close 28% more deals | 91%
- Average response time drops from 6hrs to 90sec | 85%
- Customer satisfaction increases after automation | 78%
- ambitious generalists plan to automate by 2027 | 67%
- Cost savings from reduced manual work | 43%
SOURCE: Source: McKinsey Digital 2025 | @{{BRAND_SHORT_NAME_LOWER}}"""
)
all_posts["eco_infographic_brief"] = eco_infographic_brief
time.sleep(2)

# POST 6 — Carousel (12PM)
logger.info("\n[6/10] {{BRAND_SHORT_NAME}} LI Post 2 — Carousel Caption (12:00 PM)...")
eco_post2_caption = llm_client.call_llm(
    ECO_LI_SYS,
    f"""Write the CAPTION ONLY for a LinkedIn carousel post for the {{BRAND_NAME}} company page.
Topic: A UAE business pain point that {{BRAND_SHORT_NAME}} solves. Use a fictionalized but realistic anonymous client story.
Pain point area: businesses in Dubai manually handling {selected_service} workflows and losing time/money.

Caption structure:
- Opening hook (pain point, max 10 words)
- 2-3 lines: what the client was struggling with
- 1 line: what changed after working with {{BRAND_SHORT_NAME}}
- CTA: "Save this" or "DM us to learn more"
- Max 5 lines total. Professional agency voice.
""",
    fallback_text=f"A Dubai real estate agency was losing 40% of their WhatsApp leads to competitors\n\nThey had the traffic. They had the listings. But every time a lead messaged after business hours, it went unanswered until morning.\n\nWe rebuilt their lead capture system using AI automation. Now every inquiry gets an instant, personalized reply at any hour.\n\nThe result: 3x more qualified conversations reaching their sales team.\n\nSwipe to see the exact system we built.\n\nDM us to learn more — link in bio"
)
all_posts["eco_li_post_2"] = eco_post2_caption
time.sleep(2)

# POST 7 — Social Proof / CTA (3PM)
logger.info("\n[7/10] {{BRAND_SHORT_NAME}} LI Post 3 — Social Proof CTA (3:00 PM)...")
eco_post3 = llm_client.call_llm(
    ECO_LI_SYS,
    f"""Write a short LinkedIn text post for the {{BRAND_NAME}} company page.
Type: Industry stat + agency angle + strong CTA.
Use one specific, real-feeling stat related to AI adoption in UAE or GCC businesses.
Tie the stat to what {{BRAND_SHORT_NAME}} does and why UAE founders should care.
100-200 words. Professional agency voice. End with a strong CTA.
""",
    fallback_text="UAE businesses that automate at least one sales workflow close deals 28% faster than those that don't\n\nThat stat is from McKinsey's 2025 Digital report. And it tracks with what we see working with Dubai and GCC founders.\n\nThe gap isn't technology. Every tool exists. The gap is implementation.\n\nMost UAE businesses know they need automation. Few know where to start without breaking their existing operations.\n\nThat's exactly the problem {{BRAND_SHORT_NAME}} was built to solve.\n\nWe audit your current workflow, identify the highest-ROI automation opportunity, and build it in a way your team will actually use.\n\nBook a free audit — link in bio\n\nWe're currently accepting 4 new clients this month."
)
all_posts["eco_li_post_3"] = eco_post3
time.sleep(2)


# ECO POST 4 (12AM)
logger.info("\n[15/18] {{BRAND_SHORT_NAME}} Post 4 (12:00 AM)...")
eco_post4 = llm_client.call_llm(ECO_LI_SYS, f"Write a short post about AI working 24/7 for businesses. 100-200 words. Reference: {news_summary}")
all_posts["eco_post_4"] = eco_post4

# ECO POST 5 (3AM)
logger.info("\n[16/18] {{BRAND_SHORT_NAME}} Post 5 (3:00 AM)...")
eco_post5 = llm_client.call_llm(ECO_LI_SYS, f"Write a data-driven post and an IMAGE BRIEF based on AI automation statistics. Use this AI news: {news_summary}. Output format:\nIMAGE BRIEF:\n[detailed prompt]\n\nCAPTION:\n[The post content]")
all_posts["eco_post_5"] = eco_post5

# ECO POST 6 (6AM)
logger.info("\n[17/18] {{BRAND_SHORT_NAME}} Post 6 (6:00 AM)...")
eco_post6 = llm_client.call_llm(ECO_LI_SYS, f"Write a morning tip for UAE businesses about automation. 100-200 words.")
all_posts["eco_post_6"] = eco_post6

# ECO POST 7 (6PM)
logger.info("\n[18/18] {{BRAND_SHORT_NAME}} Post 7 (6:00 PM)...")
eco_post7 = llm_client.call_llm(ECO_LI_SYS, f"Write an evening post wrapping up business operations and letting AI take over. 100-200 words.")
all_posts["eco_post_7"] = eco_post7

# ECO POST 8 (9PM)
logger.info("\n[19/18] {{BRAND_SHORT_NAME}} Post 8 (9:00 PM)...")
eco_post8 = llm_client.call_llm(ECO_LI_SYS, f"Write an insightful post and an IMAGE BRIEF based on Reddit business discussions: {reddit_summary}. Output format:\nIMAGE BRIEF:\n[detailed prompt]\n\nCAPTION:\n[The post content]")
all_posts["eco_post_8"] = eco_post8

# ============================================================
# GENERATE ECOTRUSTIA INSTAGRAM POSTS (3 posts — Slack only)
# ============================================================
print("\n" + "="*50)
logger.info("GENERATING ECOTRUSTIA INSTAGRAM POSTS (3 — Slack delivery)")
print("="*50)

ECO_IG_SYS = f"You are {{BRAND_NAME}}' Instagram content writer.\n\n{ECOTRUSTIA_BIO}\n\n{ECO_IG_RULES}"

# IG POST 1 — Image + Caption (10AM)
logger.info("\n[8/10] {{BRAND_SHORT_NAME}} IG Post 1 — Image + Caption (10:00 AM)...")
ig_post1_data = llm_client.call_llm(
    ECO_IG_SYS,
    f"""Write Instagram content for the {{BRAND_NAME}} account.
Slot: Educational AI tip / data fact (this replaces a Reel when video is unavailable — write for a static image post)
Visual topic: {selected_ig_visual['topic']}
Key stat to feature: {selected_ig_visual['stat']}

Output ALL of the following sections separated by labels:

IMAGE BRIEF:
[Describe the image in detail: color scheme (use {{BRAND_SHORT_NAME}} brand colors: deep purple #8B5CF6, electric blue #3B82F6, dark background), text overlay content, layout, style, mood, any icons or graphics needed. 1080x1080px square. Include @{{BRAND_SHORT_NAME_LOWER}} watermark.]

HOOK:
[1 line, max 8 words, punchy]

CAPTION:
[3-5 short sentences. Max 5 emojis total. Include UAE relevance.]

CTA:
[1 punchy line]

HASHTAGS:
[8-10 relevant hashtags on one line]
""",
    fallback_text=f"""IMAGE BRIEF:
Dark background (#0A0A0F), large bold stat "{selected_ig_visual['stat'][:40]}..." centered in white, with electric blue (#3B82F6) accent underline. Top: small {{BRAND_SHORT_NAME}} logo. Bottom: "@{{BRAND_SHORT_NAME_LOWER}} | Dubai AI Agency" in subtle grey text. Clean minimal aesthetic. 1080x1080px.

HOOK:
This one stat changes how Dubai businesses compete ⚡

CAPTION:
{selected_ig_visual['stat']} 🤖
Most UAE businesses are still doing this manually.
The ones that aren't? They're closing deals while their competitors are sleeping.
AI automation isn't the future for Dubai's top SMBs. It's the present.

CTA:
Follow @{{BRAND_SHORT_NAME_LOWER}} for daily AI insights 👇

HASHTAGS:
#DubaiAI #UAEBusiness #AIAutomation #DubaiTech #GCCBusiness #WhatsAppAutomation #UAEStartups #DubaiFounders #{{BRAND_SHORT_NAME}}AI #BusinessAutomation"""
)
all_posts["eco_ig_post_1"] = ig_post1_data
time.sleep(2)

# IG POST 2 — Carousel Caption + Slide Copy (3PM)
logger.info("\n[9/10] {{BRAND_SHORT_NAME}} IG Post 2 — Carousel Caption + Slides (3:00 PM)...")
ig_post2_data = llm_client.call_llm(
    ECO_IG_SYS,
    f"""Write Instagram carousel content for the {{BRAND_NAME}} account.
Topic: Myth-busting or service breakdown about {selected_service}.
UAE-focused. 5 slides.

Output ALL of the following:

CAROUSEL CAPTION:
[Hook line (max 8 words), then 2-3 sentence body, then CTA "Save this ⬇" and hashtags]

SLIDE 1 — HOOK:
Headline: [punchy myth or bold claim, max 8 words]
Subtext: [1 line — why this matters for UAE/Dubai]

SLIDE 2:
Headline: [myth or pain point to bust]
Body: [2-3 short sentences with the truth]

SLIDE 3:
Headline: [second point or step]
Body: [2-3 short sentences]

SLIDE 4:
Headline: [third point or benefit]
Body: [2-3 short sentences]

SLIDE 5 — CTA:
Headline: [strong close]
CTA Text: [DM us / Book a free audit / Follow for more]
Handle: @{{BRAND_SHORT_NAME_LOWER}}
""",
    fallback_text=f"""CAROUSEL CAPTION:
{selected_service} myths that cost Dubai businesses real money 💸
Swipe to see what's actually true in 2026.
Save this before your competitor figures it out ⬇

#DubaiAI #UAEBusiness #AIAutomation #DubaiTech #GCCStartups #{{BRAND_SHORT_NAME}}AI #BusinessGrowth #UAEFounders

SLIDE 1 — HOOK:
Headline: "{selected_service}" sounds expensive and complicated
Subtext: Most Dubai SMBs think that. Here's the truth.

SLIDE 2:
Headline: Myth: You need a big team to implement AI
Body: Reality: A single automation setup handles what 2 full-time staff used to do. UAE businesses are running 24/7 operations with zero extra headcount.

SLIDE 3:
Headline: Myth: It takes months to see results
Body: The fastest-moving Dubai clients we work with see measurable improvement in response times within the first week. Setup takes days, not months.

SLIDE 4:
Headline: Myth: It's only for large corporations
Body: Our clients range from solo consultants to 20-person teams. If you have a customer workflow, it can be automated. GCC SMBs are the biggest winners here.

SLIDE 5 — CTA:
Headline: Ready to see what your business could automate?
CTA Text: Book a free audit — DM us "AUDIT"
Handle: @{{BRAND_SHORT_NAME_LOWER}}"""
)
all_posts["eco_ig_post_2"] = ig_post2_data
time.sleep(2)

# IG POST 3 — Single Image + Caption (7PM)
logger.info("\n[10/10] {{BRAND_SHORT_NAME}} IG Post 3 — Quote Card (7:00 PM)...")
ig_post3_data = llm_client.call_llm(
    ECO_IG_SYS,
    f"""Write Instagram single image content for the {{BRAND_NAME}} account.
Type: Brand statement or quote card. Evening post — aspirational, punchy.

Output ALL of the following:

IMAGE BRIEF:
[Dark premium image brief: describe the visual. Quote/brand statement prominently displayed. {{BRAND_SHORT_NAME}} brand colors: deep purple #8B5CF6, electric blue #3B82F6 on dark background #0A0A0F. Dubai skyline silhouette or minimal abstract elements optional. @{{BRAND_SHORT_NAME_LOWER}} watermark. 1080x1080px.]

CAPTION:
[2-3 punchy lines. UAE-relevant. Max 3 emojis. Ends with CTA.]

HASHTAGS:
[8-10 relevant hashtags on one line]
""",
    fallback_text="""IMAGE BRIEF:
Deep dark background (#0A0A0F) with subtle purple gradient glow from bottom left. Large centered bold white text: "Your competitors aren't waiting." Below in electric blue (#3B82F6): "Neither should you." {{BRAND_NAME}} logo top center. "@{{BRAND_SHORT_NAME_LOWER}} | Dubai AI Agency" small text bottom. Clean, premium, minimal. 1080x1080px.

CAPTION:
The gap between you and your competitor is closing every day they automate and you don't. 🔥
UAE businesses that move fast on AI are already seeing the results.
Book a free audit — link in bio.

HASHTAGS:
#DubaiAI #UAEBusiness #AIAutomation #DubaiEntrepreneur #GCCBusiness #{{BRAND_SHORT_NAME}}AI #DubaiStartups #BusinessGrowthUAE #AIAgency #DigitalDubai"""
)
all_posts["eco_ig_post_3"] = ig_post3_data
time.sleep(2)

# ============================================================
# GENERATE CAROUSEL JSONS
# ============================================================
print("\n" + "="*50)
logger.info("GENERATING CAROUSEL JSON DATA")
print("="*50)

# {{AUTHOR_NAME}} Carousel JSON
logger.info("\nGenerating {{AUTHOR_NAME}} carousel slides JSON...")
ahmed_carousel_json_str = llm_client.call_llm(
    "You are a JSON generator. Output ONLY valid raw JSON, no markdown, no explanations.",
    f"""Based on this carousel caption for {{AUTHOR_NAME}}'s LinkedIn, generate 7 slide JSON configs.

Caption: {post3_caption}
Story topic: {selected_story}

Your JSON must follow this exact structure:
{{
  "1": {{
    "HEADER_LABEL": "AHMED ALI",
    "HOOK_PART_1": "[3-5 words]",
    "HOOK_PART_2": "[3-5 words]",
    "HOOK_EMPHASIS": "[1-2 WORDS IN CAPS]",
    "SUBTITLE": "[1-2 sentences setting up the story]"
  }},
  "2": {{
    "PILL_LABEL": "[STEP 01 or theme]",
    "EYEBROW": "[context label]",
    "HEADLINE_PART_1": "[3-4 words]",
    "HEADLINE_PART_2": "[3-4 words]",
    "HEADLINE_EMPHASIS": "[1-2 CAPS WORDS]",
    "SUBHEAD": "[1 supporting line]",
    "BODY_TEXT": "[2-3 sentences with specific detail]"
  }},
  "3": {{ "HEADER_LABEL": "...", "HUGE_STAT": "...", "CIRCLE_WORD_1": "...", "CIRCLE_WORD_2": "...", "HEADLINE_PART_1": "...", "HEADLINE_PART_2": "...", "HEADLINE_EMPHASIS": "...", "BODY_TEXT": "..." }},
  "4": {{ "PILL_LABEL": "...", "EYEBROW": "...", "HEADLINE_PART_1": "...", "HEADLINE_PART_2": "...", "HEADLINE_EMPHASIS": "...", "SUBHEAD": "...", "BODY_TEXT": "..." }},
  "5": {{ "HEADER_LABEL": "...", "HUGE_STAT": "...", "CIRCLE_WORD_1": "...", "CIRCLE_WORD_2": "...", "HEADLINE_PART_1": "...", "HEADLINE_PART_2": "...", "HEADLINE_EMPHASIS": "...", "BODY_TEXT": "..." }},
  "6": {{ "HEADER_LABEL": "...", "HUGE_STAT": "...", "HEADLINE_PART_1": "...", "HEADLINE_PART_2": "...", "HEADLINE_EMPHASIS": "...", "SUBHEAD": "...", "BODY_TEXT": "..." }},
  "7": {{
    "HEADLINE_PART_1": "Follow for more",
    "HEADLINE_PART_2": "builder breakdowns",
    "HEADLINE_EMPHASIS": "FOLLOW",
    "SUBHEAD": "{{AUTHOR_NAME}} | {{BRAND_NAME}} | Building in public from Dubai"
  }}
}}

Fill in all values based on the story topic. Make slide content specific and actionable.
""",
    fallback_text=None,
    max_tokens=2000
)

if ahmed_carousel_json_str:
    try:
        clean = ahmed_carousel_json_str.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        if clean.endswith("```"):
            clean = clean[:-3]
        ahmed_carousel = json.loads(clean.strip())
        with open("./carousel_data.json", "w") as f:
            json.dump(ahmed_carousel, f, indent=2)
        logger.info("  ✓ Saved carousel_data.json ({{AUTHOR_NAME}})")
    except Exception as e:
        logger.info(f"  ✗ {{AUTHOR_NAME}} carousel JSON parse error: {e}")

time.sleep(2)

# {{BRAND_SHORT_NAME}} Carousel JSON
logger.info("\nGenerating {{BRAND_SHORT_NAME}} carousel slides JSON...")
eco_carousel_json_str = llm_client.call_llm(
    "You are a JSON generator. Output ONLY valid raw JSON, no markdown, no explanations.",
    f"""Based on this {{BRAND_SHORT_NAME}} LinkedIn carousel caption, generate 7 slide JSON configs.

Caption: {eco_post2_caption}
Service: {selected_service}

Follow this exact structure (same as above but {{BRAND_SHORT_NAME}} agency tone):
{{
  "1": {{
    "HEADER_LABEL": "ECOTRUSTIA SOLUTIONS",
    "HOOK_PART_1": "[pain point 3-5 words]",
    "HOOK_PART_2": "[pain point 3-5 words]",
    "HOOK_EMPHASIS": "[1-2 CAPS WORDS]",
    "SUBTITLE": "[1-2 sentences about the UAE business problem]"
  }},
  "2": {{ "PILL_LABEL": "...", "EYEBROW": "THE PROBLEM", "HEADLINE_PART_1": "...", "HEADLINE_PART_2": "...", "HEADLINE_EMPHASIS": "...", "SUBHEAD": "...", "BODY_TEXT": "..." }},
  "3": {{ "HEADER_LABEL": "...", "HUGE_STAT": "...", "CIRCLE_WORD_1": "...", "CIRCLE_WORD_2": "...", "HEADLINE_PART_1": "...", "HEADLINE_PART_2": "...", "HEADLINE_EMPHASIS": "...", "BODY_TEXT": "..." }},
  "4": {{ "PILL_LABEL": "...", "EYEBROW": "THE SOLUTION", "HEADLINE_PART_1": "...", "HEADLINE_PART_2": "...", "HEADLINE_EMPHASIS": "...", "SUBHEAD": "...", "BODY_TEXT": "..." }},
  "5": {{ "HEADER_LABEL": "...", "HUGE_STAT": "...", "CIRCLE_WORD_1": "...", "CIRCLE_WORD_2": "...", "HEADLINE_PART_1": "...", "HEADLINE_PART_2": "...", "HEADLINE_EMPHASIS": "...", "BODY_TEXT": "..." }},
  "6": {{ "HEADER_LABEL": "...", "HUGE_STAT": "...", "HEADLINE_PART_1": "...", "HEADLINE_PART_2": "...", "HEADLINE_EMPHASIS": "...", "SUBHEAD": "...", "BODY_TEXT": "..." }},
  "7": {{
    "HEADLINE_PART_1": "Book a free audit",
    "HEADLINE_PART_2": "start automating today",
    "HEADLINE_EMPHASIS": "FREE AUDIT",
    "SUBHEAD": "{{BRAND_NAME}} | Dubai AI Agency | @{{BRAND_SHORT_NAME_LOWER}}"
  }}
}}
""",
    fallback_text=None,
    max_tokens=2000
)

if eco_carousel_json_str:
    try:
        clean = eco_carousel_json_str.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        if clean.endswith("```"):
            clean = clean[:-3]
        eco_carousel = json.loads(clean.strip())
        with open("./carousel_data_eco.json", "w") as f:
            json.dump(eco_carousel, f, indent=2)
        logger.info("  ✓ Saved carousel_data_eco.json ({{BRAND_SHORT_NAME}})")
    except Exception as e:
        logger.info(f"  ✗ {{BRAND_SHORT_NAME}} carousel JSON parse error: {e}")

time.sleep(2)

# Infographic JSON
logger.info("\nGenerating infographic JSON...")
infographic_json_str = llm_client.call_llm(
    "You are a JSON generator. Output ONLY valid raw JSON, no markdown, no explanations.",
    f"""Based on this infographic brief, generate the infographic JSON config.

Brief:
{eco_infographic_brief}

Output exactly this structure:
{{
  "title_main": "[main title from brief]",
  "title_span": "[subtitle]",
  "subtitle": "[1-line supporting description]",
  "badge": "[emoji + label]",
  "date_label": "[Source label]",
  "takeaway_num": "[key stat number/value]",
  "takeaway_text": "[what the stat means, 1 sentence]",
  "source": "[Source: ... | @{{BRAND_SHORT_NAME_LOWER}}]",
  "bars": [
    {{ "label": "[bar label]", "value": "[XX%]", "color": "#E63946" }},
    {{ "label": "[bar label]", "value": "[XX%]", "color": "#D9785B" }},
    {{ "label": "[bar label]", "value": "[XX%]", "color": "#E8A33D" }},
    {{ "label": "[bar label]", "value": "[XX%]", "color": "#5E6AD2" }},
    {{ "label": "[bar label]", "value": "[XX%]", "color": "#5A5A5A" }}
  ]
}}
Fill all values from the brief. Use colors as specified.
""",
    fallback_text=None,
    max_tokens=1000
)

if infographic_json_str:
    try:
        clean = infographic_json_str.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        if clean.endswith("```"):
            clean = clean[:-3]
        infographic_data = json.loads(clean.strip())
        with open("./infographic_data.json", "w") as f:
            json.dump(infographic_data, f, indent=2)
        logger.info("  ✓ Saved infographic_data.json")
    except Exception as e:
        logger.info(f"  ✗ Infographic JSON parse error: {e}")

# ============================================================
# SAVE OUTPUT FILES
# ============================================================
print("\n" + "="*50)
logger.info("SAVING OUTPUT FILES")
print("="*50)

# {{AUTHOR_NAME}} LinkedIn text file
ahmed_txt = f"""AHMED ALI — LINKEDIN POSTS — {date_str}
Generated: {datetime.datetime.now().isoformat()}
Schedule Date: {sched_str}
==============================================================================

==============================================================================
POST 1 — BUILDER STORY [9:00 AM IST | Slot: Text-only]
==============================================================================
{all_posts.get('ahmed_post_1', '[GENERATION FAILED]')}


==============================================================================
POST 2 — AI HOT TAKE [12:00 PM IST | Slot: Text-only]
==============================================================================
{all_posts.get('ahmed_post_2', '[GENERATION FAILED]')}


==============================================================================
POST 3 — CAROUSEL CAPTION [3:00 PM IST | Slot: Carousel PDF]
==============================================================================
{all_posts.get('ahmed_post_3_caption', '[GENERATION FAILED]')}
[CAROUSEL PDF: carousel-routine/output/{date_str}/carousel-branded/]


==============================================================================
POST 4 — ENGAGEMENT [6:00 PM IST | Slot: Text-only]
==============================================================================
{all_posts.get('ahmed_post_4', '[GENERATION FAILED]')}

"""

with open(f"{{AUTHOR_NAME_LOWER}}_posts_{date_compact}.txt", "w") as f:
    f.write(ahmed_txt)
with open("{{AUTHOR_NAME_LOWER}}_posts_today.txt", "w") as f:
    f.write(ahmed_txt)
logger.info(f"  ✓ {{AUTHOR_NAME_LOWER}}_posts_{date_compact}.txt")

# {{BRAND_SHORT_NAME}} LinkedIn text file
eco_li_txt = f"""ECOTRUSTIA SOLUTIONS — LINKEDIN POSTS — {date_str}
Generated: {datetime.datetime.now().isoformat()}
Schedule Date: {sched_str}
Service Spotlight: {selected_service}
==============================================================================

==============================================================================
POST 1 — SERVICE EDUCATION + INFOGRAPHIC [9:00 AM IST]
==============================================================================
{all_posts.get('eco_li_post_1', '[GENERATION FAILED]')}

--- INFOGRAPHIC BRIEF ---
{all_posts.get('eco_infographic_brief', '[GENERATION FAILED]')}
[INFOGRAPHIC PNG: linkedin-infographic-{date_compact}.png]


==============================================================================
POST 2 — CAROUSEL CAPTION [12:00 PM IST]
==============================================================================
{all_posts.get('eco_li_post_2', '[GENERATION FAILED]')}
[CAROUSEL PDF: carousel-routine/output/{date_str}/carousel-eco/]


==============================================================================
POST 3 — SOCIAL PROOF + CTA [3:00 PM IST]
==============================================================================
{all_posts.get('eco_li_post_3', '[GENERATION FAILED]')}

"""

with open(f"{{BRAND_SHORT_NAME_LOWER}}_linkedin_posts_{date_compact}.txt", "w") as f:
    f.write(eco_li_txt)
with open("{{BRAND_SHORT_NAME_LOWER}}_linkedin_posts_today.txt", "w") as f:
    f.write(eco_li_txt)
logger.info(f"  ✓ {{BRAND_SHORT_NAME_LOWER}}_linkedin_posts_{date_compact}.txt")

# {{BRAND_SHORT_NAME}} Instagram text file
eco_ig_txt = f"""ECOTRUSTIA SOLUTIONS — INSTAGRAM POSTS — {date_str}
Generated: {datetime.datetime.now().isoformat()}
NOTE: Instagram posts delivered to Slack for manual posting.
==============================================================================

==============================================================================
IG POST 1 — IMAGE + CAPTION [10:00 AM IST]
NOTE: If no Reel available, use the IMAGE BRIEF below to generate a static image.
      Ask Antigravity to generate this image for you.
==============================================================================
{all_posts.get('eco_ig_post_1', '[GENERATION FAILED]')}


==============================================================================
IG POST 2 — CAROUSEL [3:00 PM IST]
==============================================================================
{all_posts.get('eco_ig_post_2', '[GENERATION FAILED]')}


==============================================================================
IG POST 3 — QUOTE CARD / BRAND IMAGE [7:00 PM IST]
NOTE: Ask Antigravity to generate this image using the IMAGE BRIEF below.
==============================================================================
{all_posts.get('eco_ig_post_3', '[GENERATION FAILED]')}

"""

with open(f"{{BRAND_SHORT_NAME_LOWER}}_instagram_posts_{date_compact}.txt", "w") as f:
    f.write(eco_ig_txt)
with open("{{BRAND_SHORT_NAME_LOWER}}_instagram_posts_today.txt", "w") as f:
    f.write(eco_ig_txt)
logger.info(f"  ✓ {{BRAND_SHORT_NAME_LOWER}}_instagram_posts_{date_compact}.txt")

# Combined posts_today.json (for scheduling scripts)
posts_json = {
    "date": date_str,
    "schedule_date": sched_str,
    "generated_at": datetime.datetime.now().isoformat(),
    "ahmed_linkedin": [
        {"id": 5, "slot": "12:00 AM", "type": "text", "caption": all_posts.get("ahmed_post_5", ""), "date": sched_str},
        {"id": 6, "slot": "3:00 AM", "type": "image", "image_png": "/Users/apple/.gemini/antigravity/brain/1f808839-61e5-4da2-b5f0-ff18d9b19af4/ahmed_3am_1782852382640.png", "caption": all_posts.get("ahmed_post_6", ""), "date": sched_str},
        {"id": 7, "slot": "6:00 AM", "type": "text", "caption": all_posts.get("ahmed_post_7", ""), "date": sched_str},
        {"id": 1, "slot": "9:00 AM", "type": "text", "caption": all_posts.get("ahmed_post_1", ""), "date": sched_str},
        {"id": 2, "slot": "12:00 PM", "type": "text", "caption": all_posts.get("ahmed_post_2", ""), "date": sched_str},
        {"id": 3, "slot": "3:00 PM", "type": "carousel", "caption": all_posts.get("ahmed_post_3_caption", ""),
         "carousel_pdf": f"./carousel-routine/output/{date_str}/carousel-branded/",
         "carousel_title": f"Builder Breakdown — {date_str}", "date": sched_str},
        {"id": 4, "slot": "6:00 PM", "type": "text", "caption": all_posts.get("ahmed_post_4", ""), "date": sched_str},
        {"id": 8, "slot": "9:00 PM", "type": "text", "caption": all_posts.get("ahmed_post_8", ""), "date": sched_str},
    ],
    "{{BRAND_SHORT_NAME_LOWER}}_linkedin": [
        {"id": 4, "slot": "12:00 AM", "type": "text", "caption": all_posts.get("eco_post_4", ""), "date": sched_str},
        {"id": 5, "slot": "3:00 AM", "type": "image", "image_png": "/Users/apple/.gemini/antigravity/brain/1f808839-61e5-4da2-b5f0-ff18d9b19af4/eco_3am_1782852391328.png", "caption": all_posts.get("eco_post_5", ""), "date": sched_str},
        {"id": 6, "slot": "6:00 AM", "type": "text", "caption": all_posts.get("eco_post_6", ""), "date": sched_str},
        {"id": 1, "slot": "9:00 AM", "type": "infographic", "caption": all_posts.get("eco_li_post_1", ""),
         "infographic_png": f"./linkedin-infographic-{date_compact}.png", "date": sched_str},
        {"id": 2, "slot": "12:00 PM", "type": "carousel", "caption": all_posts.get("eco_li_post_2", ""),
         "carousel_pdf": f"./carousel-routine/output/{date_str}/carousel-eco/",
         "carousel_title": f"{selected_service} — {{BRAND_SHORT_NAME}}", "date": sched_str},
        {"id": 3, "slot": "3:00 PM", "type": "text", "caption": all_posts.get("eco_li_post_3", ""), "date": sched_str},
        {"id": 7, "slot": "6:00 PM", "type": "text", "caption": all_posts.get("eco_post_7", ""), "date": sched_str},
        {"id": 8, "slot": "9:00 PM", "type": "image", "image_png": "/Users/apple/.gemini/antigravity/brain/1f808839-61e5-4da2-b5f0-ff18d9b19af4/eco_9pm_1782852400858.png", "caption": all_posts.get("eco_post_8", ""), "date": sched_str},
    ],
    "{{BRAND_SHORT_NAME_LOWER}}_instagram": [
        {"id": 1, "slot": "10:00 AM", "type": "image", "raw": all_posts.get("eco_ig_post_1", "")},
        {"id": 2, "slot": "3:00 PM", "type": "carousel", "raw": all_posts.get("eco_ig_post_2", "")},
        {"id": 3, "slot": "7:00 PM", "type": "image", "raw": all_posts.get("eco_ig_post_3", "")},
    ]
}

with open("posts_today.json", "w") as f:
    json.dump(posts_json, f, indent=2)
logger.info("  ✓ posts_today.json")

# ============================================================
# FINAL SUMMARY
# ============================================================
print(f"""
{'='*60}
✓ CONTENT GENERATION COMPLETE — {date_str}
{'='*60}

AHMED LINKEDIN ({sched_str}):
  09:00 AM — Builder Story (text)
  12:00 PM — AI Hot Take (text)
  03:00 PM — Carousel (PDF — build separately)
  06:00 PM — Engagement Reflection (text)

ECOTRUSTIA LINKEDIN ({sched_str}):
  09:00 AM — {selected_service} Education + Infographic
  12:00 PM — Carousel (PDF — build separately)
  03:00 PM — Social Proof + CTA (text)

ECOTRUSTIA INSTAGRAM (Slack-delivered):
  10:00 AM — AI Fact Image + Caption
  03:00 PM — Carousel Caption + Slide Copy
  07:00 PM — Quote Card + Caption

FILES SAVED:
  {{AUTHOR_NAME_LOWER}}_posts_{date_compact}.txt
  {{BRAND_SHORT_NAME_LOWER}}_linkedin_posts_{date_compact}.txt
  {{BRAND_SHORT_NAME_LOWER}}_instagram_posts_{date_compact}.txt
  posts_today.json
  carousel_data.json ({{AUTHOR_NAME}} slides)
  carousel_data_eco.json ({{BRAND_SHORT_NAME}} slides)
  infographic_data.json

NEXT STEPS:
  1. Build carousels:   cd carousel-routine && node screenshot_all.js && node compile_pdf.js
  2. Build infographic: node cap_infographic_today.cjs
  3. Send to Slack:     python3 send_to_slack.py
  4. Schedule {{AUTHOR_NAME}}:    node schedule_{{AUTHOR_NAME_LOWER}}_posts.cjs
  5. Schedule Eco LI:   node schedule_{{BRAND_SHORT_NAME_LOWER}}_linkedin.cjs

  OR run everything:    bash run_pipeline.sh
{'='*60}
""")
