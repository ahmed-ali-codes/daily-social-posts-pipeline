import os
import json
import logging
from llm_client import LLMClient
import urllib.request
import urllib.parse
import ssl
import sys
import datetime
import traceback

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Read Gemini API key from .env
gemini_key = None
env_path = "./.env"
with open(env_path) as f:
    for line in f:
        if line.startswith("GEMINI_API_KEY="):
            gemini_key = line.strip().split("=", 1)[1]
            break

if not gemini_key:
    logger.info("Error: GEMINI_API_KEY not found in .env")
    exit(1)

# Load Reddit posts data (keep top 15 posts to stay within context limits and keep focus)
reddit_posts = []
if os.path.exists("./reddit_data.json"):
    try:
        with open("./reddit_data.json") as f:
            all_r = json.load(f)
            # Sort by simulated popularity/score or just take top
            reddit_posts = all_r[:15]
    except Exception as e:
        logger.info(f"Error loading reddit_data.json: {e}")

# Load AI News data
ai_news = []
if os.path.exists("./ai_news_data.json"):
    try:
        with open("./ai_news_data.json") as f:
            all_n = json.load(f)
            ai_news = all_n[:12]
    except Exception as e:
        logger.info(f"Error loading ai_news_data.json: {e}")

# Load infographic run-log and calculate banned formats/topics
banned_infographic_formats = []
banned_infographic_topics = []
try:
    if os.path.exists("./infographic-run-log.json"):
        with open("./infographic-run-log.json") as f:
            info_log = json.load(f)
            
        # Last 14 topics are banned
        banned_infographic_topics = [entry["topic"] for entry in info_log[-14:] if "topic" in entry]
        
        # Last 5 formats tally
        recent_formats = [entry["format"] for entry in info_log[-5:] if "format" in entry]
        if recent_formats:
            # Last format is banned
            banned_infographic_formats.append(recent_formats[-1])
            # 3+ times count in last 5 runs
            from collections import Counter
            counts = Counter(recent_formats)
            for fmt, count in counts.items():
                if count >= 3 and fmt not in banned_infographic_formats:
                    banned_infographic_formats.append(fmt)
except Exception as e:
    logger.info(f"Error loading infographic log: {e}")

# Load carousel hook log and calculate banned hook styles
banned_carousel_hooks = []
try:
    if os.path.exists("./carousel-hook-log.json"):
        with open("./carousel-hook-log.json") as f:
            car_log = json.load(f)
            
        recent_hooks = [entry["hook_style"] for entry in car_log[-7:] if "hook_style" in entry]
        if recent_hooks:
            # Last hook is banned
            banned_carousel_hooks.append(recent_hooks[-1])
            # 3+ times count in last 7 runs
            from collections import Counter
            counts = Counter(recent_hooks)
            for hook, count in counts.items():
                if count >= 3 and hook not in banned_carousel_hooks:
                    banned_carousel_hooks.append(hook)
except Exception as e:
    logger.info(f"Error loading carousel log: {e}")

print("Banned Infographic Formats:", banned_infographic_formats)
print("Banned Infographic Topics:", banned_infographic_topics)
print("Banned Carousel Hook Styles:", banned_carousel_hooks)

# Format context strings
reddit_context = ""
for i, post in enumerate(reddit_posts):
    reddit_context += f"Post {i+1} [Subreddit: {post['subreddit']}]:\nTitle: {post['title']}\nContent: {post['selftext'][:400]}...\n---\n"

ai_news_context = ""
for i, item in enumerate(ai_news):
    ai_news_context += f"News {i+1} [Source: {item['source']}]:\nTitle: {item['title']}\nDescription: {item['description'][:400]}...\nURL: {item['url']}\nDate: {item['pubDate']}\n---\n"

system_prompt = """
You are the Content Engine for two brands:
1. {{AUTHOR_NAME}} — Personal LinkedIn brand. Software engineering student at Curtin University Dubai, founder of {{BRAND_NAME}}, UAE-based builder, AI automation specialist, hackathon winner, MiniOS kernel developer, n8n automation expert.
2. {{BRAND_NAME}} — A AI's impact on work, income, skills, and the future offering: AI automation, web development, SEO, social media marketing, branding, app development, and e-commerce.

DAILY OUTPUT TARGETS:
{{AUTHOR_NAME}} Personal LinkedIn (4 posts/day):
- Post 1: Builder Story / Personal Win / Lesson (Text-only, 200-400 words)
- Post 2: AI/Tech Hot Take from UAE perspective (Text + hook list)
- Post 3: Tutorial / Framework / Breakdown (Carousel 5-8 slides)
- Post 4: Engagement bait / Question / Reflection (Text-only)

{{BRAND_SHORT_NAME}} LinkedIn Page (3 posts/day):
- Post 1: Service Education (Text + infographic)
- Post 2: Client result angle / UAE business pain point solved (Carousel)
- Post 3: Social proof hook / Industry stat / CTA (Text-only)

{{BRAND_SHORT_NAME}} Instagram (3 posts/day):
- Post 1: Educational short-form (Reel caption + hook)
- Post 2: Service breakdown or myth-busting (Carousel caption + slide copy)
- Post 3: Single image caption (Quote/brand statement + CTA)

VOICE PROFILES:
- {{AUTHOR_NAME}} Personal Voice: Casual-smart, young founder, builder journey. Uses phrases like "Here's what I learned building X", "Nobody tells you this about Y", "After 3 years of doing Z...". First-person.
- {{BRAND_SHORT_NAME}} LinkedIn Voice: Professional agency tone. Ties back to UAE/Dubai context. Leads with pain point -> solution -> proof structure.
- {{BRAND_SHORT_NAME}} Instagram Voice: Punchy, hooks under 10 words. Visual-first. Emojis allowed (max 5).

GLOBAL BANNED WORDS (NEVER USE):
game-changer, delve, dive in, leverage (as verb), paradigm, it's important to note, synergy, holistic, cutting-edge, world-class, bespoke, groundbreaking, revolutionary, unlock your potential, empower

OUTPUT FORMAT:
Output all 10 posts using the exact format and separators. Do not output any preamble.

==================================================
1. AHMED POST 1 (BUILDER STORY)
==================================================
[Text]

==================================================
2. AHMED POST 2 (HOT TAKE)
==================================================
[Text]

==================================================
3. AHMED POST 3 (CAROUSEL)
==================================================
Slide 1:
[Headline]

Slide 2:
[Text]

Slide 3:
[Text]

Slide 4:
[Text]

Slide 5:
[Text]

Slide 6:
[Text]

Slide 7:
[Text]

Slide 8:
[Text]

CAROUSEL CAPTION:
[Text]

==================================================
4. AHMED POST 4 (ENGAGEMENT)
==================================================
[Text]

==================================================
5. ECOTRUSTIA LINKEDIN POST 1 (SERVICE EDUCATION)
==================================================
[Text]
INFOGRAPHIC BRIEF:
[Brief description of visual infographic representing stats/concepts]

==================================================
6. ECOTRUSTIA LINKEDIN POST 2 (CAROUSEL)
==================================================
Slide 1:
[Headline]

Slide 2:
[Text]

Slide 3:
[Text]

Slide 4:
[Text]

Slide 5:
[Text]

Slide 6:
[Text]

Slide 7:
[Text]

Slide 8:
[Text]

CAROUSEL CAPTION:
[Text]

==================================================
7. ECOTRUSTIA LINKEDIN POST 3 (SOCIAL PROOF)
==================================================
[Text]

==================================================
8. ECOTRUSTIA INSTAGRAM POST 1 (REEL CAPTION)
==================================================
[Text]

==================================================
9. ECOTRUSTIA INSTAGRAM POST 2 (CAROUSEL CAPTION)
==================================================
[Text]
SLIDE COPY:
[Text for slides 1 to 5]

==================================================
10. ECOTRUSTIA INSTAGRAM POST 3 (SINGLE IMAGE CAPTION)
==================================================
[Text]
"""

prompt = f"""
Here are today's feeds:

REDDIT FEED:
{reddit_context}

AI NEWS FEED:
{ai_news_context}

BANNED CAROUSEL HOOK STYLES (DO NOT USE THESE FOR POST 3 CAROUSEL SLIDE 1):
{', '.join(banned_carousel_hooks) if banned_carousel_hooks else 'None'}
Please select one of the following hook styles instead: Bold Claim, Mistake Call-Out, Myth Buster, Curiosity Gap, Number Reveal, Before-After, Checklist Promise, Framework Authority, Relatable Pain.

BANNED INFOGRAPHIC FORMATS (DO NOT USE THESE FOR POST 4 INFOGRAPHIC CAPTION & VISUAL DESIGN):
{', '.join(banned_infographic_formats) if banned_infographic_formats else 'None'}
Please select one of the following formats instead: DONUT_BREAKDOWN, TIMELINE_SHIFT, COMPARISON_SPLIT, HERO_NUMBER.

BANNED INFOGRAPHIC TOPICS (DO NOT OVERLAP WITH THESE SUBJECTS FOR THE INFOGRAPHIC):
{json.dumps(banned_infographic_topics, indent=2)}

Write the 11 posts now. Remember to strictly apply all rules (third-person, no banned words, {{BRAND_SHORT_NAME}} mentions in Post 8 and Post 10).
Ensure the Carousel and Infographic captions explicitly output their chosen styles/formats (e.g. Chosen style: [style] and Chosen format: [format]) and make sure they are NOT banned!
"""

system_prompt_json = """
You are {{AUTHOR_NAME}}'s AI visual content designer.
Based on the posts generated for today, you must generate the structured JSON configuration for the Carousel and the Infographic.

Format your output as a single valid JSON object. Do NOT wrap it in any markdown code block, and do NOT include any other text before or after the JSON.
Your JSON must strictly follow this structure:
{
  "carousel": {
    "1": {
      "HEADER_LABEL": "[Slide 1 category, e.g. DISTRIBUTION]",
      "HOOK_PART_1": "[Slide 1 Hook line 1, 3-4 words]",
      "HOOK_PART_2": "[Slide 1 Hook line 2, 3-4 words]",
      "HOOK_EMPHASIS": "[Slide 1 Highlighted word]",
      "SUBTITLE": "[Slide 1 detailed explanation, under 25 words]"
    },
    "2": {
      "PILL_LABEL": "[Pill text]",
      "EYEBROW": "[Eyebrow category]",
      "HEADLINE_PART_1": "[Title start]",
      "HEADLINE_PART_2": "[Title end]",
      "HEADLINE_EMPHASIS": "[Title emphasis]",
      "SUBHEAD": "[Short subhead sentence]",
      "BODY_TEXT": "[Description sentence]"
    },
    "3": {
      "HEADER_LABEL": "[Category]",
      "HUGE_STAT": "[Stat, e.g. 90% or $1k]",
      "CIRCLE_WORD_1": "[Circle label 1]",
      "CIRCLE_WORD_2": "[Circle label 2]",
      "HEADLINE_PART_1": "[Title start]",
      "HEADLINE_PART_2": "[Title end]",
      "HEADLINE_EMPHASIS": "[Title emphasis]",
      "BODY_TEXT": "[Description sentence]"
    },
    "4": {
      "PILL_LABEL": "[Pill text]",
      "EYEBROW": "[Eyebrow category]",
      "HEADLINE_PART_1": "[Title start]",
      "HEADLINE_PART_2": "[Title end]",
      "HEADLINE_EMPHASIS": "[Title emphasis]",
      "SUBHEAD": "[Short subhead sentence]",
      "BODY_TEXT": "[Description sentence]"
    },
    "5": {
      "HEADER_LABEL": "[Category]",
      "HUGE_STAT": "[Stat, e.g. 5x]",
      "CIRCLE_WORD_1": "[Circle label 1]",
      "CIRCLE_WORD_2": "[Circle label 2]",
      "HEADLINE_PART_1": "[Title start]",
      "HEADLINE_PART_2": "[Title end]",
      "HEADLINE_EMPHASIS": "[Title emphasis]",
      "BODY_TEXT": "[Description sentence]"
    },
    "6": {
      "HEADER_LABEL": "[Category]",
      "HUGE_STAT": "[Stat]",
      "HEADLINE_PART_1": "[Title start]",
      "HEADLINE_PART_2": "[Title end]",
      "HEADLINE_EMPHASIS": "[Title emphasis]",
      "SUBHEAD": "[Short subhead sentence]",
      "BODY_TEXT": "[Description sentence]"
    },
    "7": {
      "HEADLINE_PART_1": "[Title start]",
      "HEADLINE_PART_2": "[Title end]",
      "HEADLINE_EMPHASIS": "[Title emphasis]",
      "SUBHEAD": "[Concluding call to action subhead]"
    }
  },
  "infographic": {
    "title_main": "[Main Title]",
    "title_span": "[Highlighted Word]",
    "subtitle": "[Subtext description]",
    "badge": "📊 [Badge label]",
    "date_label": "[Month Year Report]",
    "takeaway_num": "[Stat, e.g. 95%]",
    "takeaway_text": "[Summary insight sentence]",
    "source": "Source: [Sources] | @{{BRAND_SHORT_NAME_LOWER}}",
    "bars": [
      { "label": "[Row 1 Label]", "value": "95%", "color": "#E63946" },
      { "label": "[Row 2 Label]", "value": "80%", "color": "#D9785B" },
      { "label": "[Row 3 Label]", "value": "75%", "color": "#E8A33D" },
      { "label": "[Row 4 Label]", "value": "64%", "color": "#5E6AD2" },
      { "label": "[Row 5 Label]", "value": "63%", "color": "#5A5A5A" },
      { "label": "[Row 6 Label]", "value": "40%", "color": "#111111" }
    ]
  }
}
"""

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
headers = {
    "Content-Type": "application/json"
}

def make_call(system_p, user_p, max_t=4000):
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": user_p
                    }
                ]
            }
        ],
        "systemInstruction": {
            "parts": [
                {
                    "text": system_p
                }
            ]
        },
        "generationConfig": {
            "maxOutputTokens": max_t
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    try:
        logger.info("Calling Google Gemini 3.5 Flash...")
        with urllib.request.urlopen(req, context=ctx) as res:
            resp = json.loads(res.read().decode("utf-8"))
            if resp and isinstance(resp, dict) and "candidates" in resp and len(resp["candidates"]) > 0:
                return resp["candidates"][0]["content"]["parts"][0]["text"]
            else:
                logger.info(f"Gemini returned unexpected response: {resp}")
    except urllib.error.HTTPError as e:
        logger.info(f"HTTP Error calling Gemini: {e.code} - {e.reason}")
        try:
            logger.info("Response body:", e.read().decode("utf-8"))
        except Exception as read_err:
            print("Failed to read error body:", read_err)
    except Exception as e:
        traceback.print_exc()
        logger.info(f"Error calling Gemini: {e}")
    return None

# Step 1: Generate LinkedIn text posts
logger.info("Starting Step 1: Generating text posts...")
post_text = make_call(system_prompt, prompt, max_t=4000)

if not post_text:
    logger.info("Error: Failed to generate LinkedIn posts.")
    sys.exit(1)

llm_client = LLMClient(openrouter_key, '')

# Save posts text
date_compact = datetime.date.today().isoformat().replace("-", "")
with open("./linkedin_posts_today.txt", "w") as f:
    f.write(post_text)
with open(f"./linkedin_posts_{date_compact}.txt", "w") as f:
    f.write(post_text)
logger.info(f"Text posts saved to linkedin_posts_{date_compact}.txt")

# Step 2: Extract visuals JSON data based on generated text posts
logger.info("Starting Step 2: Extracting visuals layout JSON...")
json_prompt = f"Here are the generated LinkedIn posts:\n\n{post_text}\n\nGenerate the Carousel and Infographic JSON now."
json_data_str = make_call(system_prompt_json, json_prompt, max_t=2000)

if json_data_str:
    try:
        # Clean up code blocks markdown if LLM wrapped it
        json_data_str = json_data_str.strip()
        if json_data_str.startswith("```json"):
            json_data_str = json_data_str[7:]
        elif json_data_str.startswith("```"):
            json_data_str = json_data_str[3:]
        if json_data_str.endswith("```"):
            json_data_str = json_data_str[:-3]
        json_data_str = json_data_str.strip()
        
        layout_data = json.loads(json_data_str)
        
        # Save carousel_data.json
        with open("./carousel_data.json", "w") as f:
            json.dump(layout_data.get("carousel", {}), f, indent=2)
        logger.info("Saved carousel_data.json")
        
        # Save infographic_data.json
        with open("./infographic_data.json", "w") as f:
            json.dump(layout_data.get("infographic", {}), f, indent=2)
        logger.info("Saved infographic_data.json")
        
    except Exception as e:
        logger.info(f"Error parsing JSON block from response: {e}")
        logger.info("Raw JSON string attempted:")
        print(json_data_str[:1000])
else:
    logger.info("Warning: No JSON data generated in Step 2.")
