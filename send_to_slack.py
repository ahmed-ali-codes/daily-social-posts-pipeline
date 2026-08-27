#!/usr/bin/env python3
"""
Slack Delivery — All Channels
==============================
Sends all 10 daily posts organized by channel to Slack.
Also uploads carousel PDFs, infographic PNG, and raw text files.
Bot Token: xoxb-... (from SLACK_BOT_TOKEN in .env)
"""

import os
import json
import urllib.request
import urllib.parse
import datetime

# ============================================================
# ENV LOADING
# ============================================================
env_vars = {}
with open(os.path.join(os.path.dirname(__file__), ".env")) as f:
    for line in f:
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env_vars[k.strip()] = v.strip()

slack_token = env_vars.get("SLACK_BOT_TOKEN", "")
channel = env_vars.get("SLACK_CHANNEL_ID", "C0BD1BYFK0D")

if not slack_token:
    print("ERROR: SLACK_BOT_TOKEN not found in .env")
    exit(1)

date_str = datetime.date.today().isoformat()
date_compact = date_str.replace("-", "")

# ============================================================
# SLACK HELPERS
# ============================================================
def slack_post(text, blocks=None):
    """Post a message to Slack."""
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {slack_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "channel": channel,
        "text": text,
        "unfurl_links": False,
        "unfurl_media": False
    }
    if blocks:
        payload["blocks"] = blocks
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                  headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            resp = json.loads(res.read().decode("utf-8"))
            if not resp.get("ok"):
                print(f"  Slack error: {resp.get('error')}")
            else:
                print(f"  ✓ Message sent")
    except Exception as e:
        print(f"  ✗ Exception sending message: {e}")


def slack_upload(file_path, file_name, comment):
    """Upload a file to Slack using the v2 upload API."""
    if not file_path or not os.path.exists(file_path):
        print(f"  ✗ File not found: {file_path}")
        return

    size = os.path.getsize(file_path)
    print(f"  Uploading {file_name} ({size} bytes)...")

    # Step 1: Get upload URL
    url = "https://slack.com/api/files.getUploadURLExternal"
    headers = {"Authorization": f"Bearer {slack_token}",
               "Content-Type": "application/x-www-form-urlencoded"}
    data = urllib.parse.urlencode({"filename": file_name, "length": size}).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            resp = json.loads(res.read().decode())
            if not resp.get("ok"):
                print(f"  ✗ Upload URL error: {resp.get('error')}")
                return
            upload_url = resp["upload_url"]
            file_id = resp["file_id"]
    except Exception as e:
        print(f"  ✗ Get upload URL error: {e}")
        return

    # Step 2: Upload file bytes
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
        req = urllib.request.Request(upload_url, data=file_data, method="POST")
        with urllib.request.urlopen(req, timeout=60) as res:
            if res.status != 200:
                print(f"  ✗ File byte upload failed (status {res.status})")
                return
    except Exception as e:
        print(f"  ✗ File upload error: {e}")
        return

    # Step 3: Complete upload
    url = "https://slack.com/api/files.completeUploadExternal"
    headers = {"Authorization": f"Bearer {slack_token}",
               "Content-Type": "application/json; charset=utf-8"}
    payload = {"files": [{"id": file_id, "title": file_name}],
               "channel_id": channel, "initial_comment": comment}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                  headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            resp = json.loads(res.read().decode())
            if resp.get("ok"):
                print(f"  ✓ Uploaded: {file_name}")
            else:
                print(f"  ✗ Complete upload error: {resp.get('error')}")
    except Exception as e:
        print(f"  ✗ Complete upload exception: {e}")


def load_txt(filename):
    """Load a text file, return empty string if not found."""
    if os.path.exists(filename):
        with open(filename) as f:
            return f.read().strip()
    return ""


def load_json(filename):
    """Load posts_today.json."""
    if os.path.exists(filename):
        with open(filename) as f:
            return json.load(f)
    return {}

# ============================================================
# LOAD TODAY'S POSTS
# ============================================================
posts_data = load_json("posts_today.json")
sched_date = posts_data.get("schedule_date", "tomorrow")

# ============================================================
# SECTION 1: HEADER
# ============================================================
print("\n=== SENDING TO SLACK ===")
print("\n[Header]")
slack_post(
    f"📅 *Daily Content Drop — {date_str}*\n"
    f"10 posts generated across 3 channels. Posts scheduled for *{sched_date}*.\n"
    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
)

# ============================================================
# SECTION 2: AHMED PERSONAL LINKEDIN (4 posts)
# ============================================================
print("\n[{{AUTHOR_NAME}} LinkedIn — 4 posts]")
slack_post(
    "🧑‍💻 *AHMED ALI — PERSONAL LINKEDIN*\n"
    "4 posts | linkedin.com/in/ahmed-ali-jawad\n"
    f"Scheduled: {sched_date}\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
)

{{AUTHOR_NAME_LOWER}}_posts = posts_data.get("ahmed_linkedin", [])
slot_labels = {
    "9:00 AM": "Post 1 — Builder Story 🏗️",
    "12:00 PM": "Post 2 — AI Hot Take ⚡",
    "3:00 PM": "Post 3 — Carousel 🎠",
    "6:00 PM": "Post 4 — Engagement 💬",
}

for post in {{AUTHOR_NAME_LOWER}}_posts:
    slot = post.get("slot", "")
    label = slot_labels.get(slot, f"Post {post['id']}")
    caption = post.get("caption", "").strip()
    if not caption:
        continue
    msg = f"*{label} | {slot} IST*\n\n{caption}"
    if post.get("type") == "carousel":
        msg += f"\n\n📎 _Carousel PDF will be attached separately_"
    slack_post(msg)

# ============================================================
# SECTION 3: ECOTRUSTIA LINKEDIN (3 posts)
# ============================================================
print("\n[{{BRAND_SHORT_NAME}} LinkedIn — 3 posts]")
slack_post(
    "🏢 *ECOTRUSTIA SOLUTIONS — LINKEDIN PAGE*\n"
    "3 posts | linkedin.com/company/{{BRAND_SHORT_NAME_LOWER}}-solutions\n"
    f"Scheduled: {sched_date}\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
)

eco_li_posts = posts_data.get("{{BRAND_SHORT_NAME_LOWER}}_linkedin", [])
eco_li_labels = {
    "9:00 AM": "Post 1 — Service Education + Infographic 📊",
    "12:00 PM": "Post 2 — Carousel 🎠",
    "3:00 PM": "Post 3 — Social Proof + CTA 🎯",
}

# Load full {{BRAND_SHORT_NAME}} LI file for infographic brief
eco_li_full = load_txt(f"{{BRAND_SHORT_NAME_LOWER}}_linkedin_posts_{date_compact}.txt")

for post in eco_li_posts:
    slot = post.get("slot", "")
    label = eco_li_labels.get(slot, f"Post {post['id']}")
    caption = post.get("caption", "").strip()
    if not caption:
        continue
    msg = f"*{label} | {slot} IST*\n\n{caption}"
    if post.get("type") == "infographic":
        msg += f"\n\n📎 _Infographic PNG will be attached separately_"
    elif post.get("type") == "carousel":
        msg += f"\n\n📎 _Carousel PDF will be attached separately_"
    slack_post(msg)

# ============================================================
# SECTION 4: ECOTRUSTIA INSTAGRAM (3 posts — manual posting)
# ============================================================
print("\n[{{BRAND_SHORT_NAME}} Instagram — 3 posts]")
slack_post(
    "📸 *ECOTRUSTIA SOLUTIONS — INSTAGRAM*\n"
    "3 posts | @{{BRAND_SHORT_NAME_LOWER}}\n"
    "⚠️ *Manual posting required* — copy below content to Instagram\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
)

eco_ig_posts = posts_data.get("{{BRAND_SHORT_NAME_LOWER}}_instagram", [])
ig_labels = {
    1: "IG Post 1 — Image + Caption 🖼️ | 10:00 AM IST",
    2: "IG Post 2 — Carousel 🎠 | 3:00 PM IST",
    3: "IG Post 3 — Quote Card 💬 | 7:00 PM IST",
}

for post in eco_ig_posts:
    pid = post.get("id", 0)
    label = ig_labels.get(pid, f"IG Post {pid}")
    raw = post.get("raw", "").strip()
    if not raw:
        continue

    note = ""
    if post.get("type") == "image":
        note = "\n\n📌 *To generate the image: ask Antigravity to generate it using the IMAGE BRIEF above*"

    slack_post(f"*{label}*\n\n{raw}{note}")

# ============================================================
# SECTION 5: UPLOAD FILES
# ============================================================
print("\n[Uploading files]")

# Upload {{AUTHOR_NAME}}'s raw text file
slack_upload(
    f"{{AUTHOR_NAME_LOWER}}_posts_{date_compact}.txt",
    f"{{AUTHOR_NAME_LOWER}}_posts_{date_compact}.txt",
    f"📄 {{AUTHOR_NAME}} LinkedIn — Raw text ({date_str})"
)

# Upload {{BRAND_SHORT_NAME}} LI raw text file
slack_upload(
    f"{{BRAND_SHORT_NAME_LOWER}}_linkedin_posts_{date_compact}.txt",
    f"{{BRAND_SHORT_NAME_LOWER}}_linkedin_posts_{date_compact}.txt",
    f"📄 {{BRAND_SHORT_NAME}} LinkedIn — Raw text ({date_str})"
)

# Upload {{BRAND_SHORT_NAME}} Instagram raw text file
slack_upload(
    f"{{BRAND_SHORT_NAME_LOWER}}_instagram_posts_{date_compact}.txt",
    f"{{BRAND_SHORT_NAME_LOWER}}_instagram_posts_{date_compact}.txt",
    f"📄 {{BRAND_SHORT_NAME}} Instagram — Raw text + Image Briefs ({date_str})"
)

# Upload {{AUTHOR_NAME}}'s carousel PDF (look for it in output dir)
ahmed_carousel_dir = f"./carousel-routine/output/{date_str}/carousel-branded"
if os.path.exists(ahmed_carousel_dir):
    pdfs = sorted([f for f in os.listdir(ahmed_carousel_dir) if f.endswith(".pdf")])
    if pdfs:
        pdf_path = os.path.join(ahmed_carousel_dir, pdfs[-1])
        slack_upload(pdf_path, f"ahmed-carousel-{date_compact}.pdf",
                     f"🎠 {{AUTHOR_NAME}} LinkedIn Carousel PDF | Post 3 (3:00 PM IST)")
        # Also upload individual slide PNGs
        slides = sorted([f for f in os.listdir(ahmed_carousel_dir)
                         if f.startswith("slide-") and f.endswith(".png")])
        for slide_fn in slides:
            num = slide_fn.split("-")[1].split(".")[0]
            slack_upload(os.path.join(ahmed_carousel_dir, slide_fn), slide_fn,
                         f"Slide {num}/{len(slides)}")

# Upload {{BRAND_SHORT_NAME}} carousel PDF
eco_carousel_dir = f"./carousel-routine/output/{date_str}/carousel-eco"
if os.path.exists(eco_carousel_dir):
    pdfs = sorted([f for f in os.listdir(eco_carousel_dir) if f.endswith(".pdf")])
    if pdfs:
        pdf_path = os.path.join(eco_carousel_dir, pdfs[-1])
        slack_upload(pdf_path, f"{{BRAND_SHORT_NAME_LOWER}}-carousel-{date_compact}.pdf",
                     f"🎠 {{BRAND_SHORT_NAME}} LinkedIn Carousel PDF | Post 2 (12:00 PM IST)")

# Upload {{BRAND_SHORT_NAME}} infographic PNG
infographic_path = f"./linkedin-infographic-{date_compact}.png"
if os.path.exists(infographic_path):
    slack_upload(infographic_path, f"{{BRAND_SHORT_NAME_LOWER}}-infographic-{date_compact}.png",
                 f"📊 {{BRAND_SHORT_NAME}} LinkedIn Infographic PNG | Post 1 (9:00 AM IST)")

# ============================================================
# FOOTER
# ============================================================
slack_post(
    f"✅ *Content drop complete — {date_str}*\n"
    f"Schedule: `node schedule_{{AUTHOR_NAME_LOWER}}_posts.cjs` | `node schedule_{{BRAND_SHORT_NAME_LOWER}}_linkedin.cjs`\n"
    f"Instagram: Post manually from the IG content above. Ask Antigravity to generate images.\n"
    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
)

print("\n✓ All Slack delivery complete!")
