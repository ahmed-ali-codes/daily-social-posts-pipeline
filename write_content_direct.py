import json
import datetime
import os

date_str = '2026-07-08'
sched_date = '07/08/2026'

# {{AUTHOR_NAME}}'s Posts (skipped)
{{AUTHOR_NAME_LOWER}}_posts = []

# {{BRAND_SHORT_NAME}}'s 2 Posts
eco_posts = [
  {
    "id": 1, "slot": "10:00 AM", "type": "carousel", "date": sched_date, "post_now": True,
    "carousel_pdf": "/Users/apple/Documents/{{BRAND_SHORT_NAME}}-data/daily-linkedin-posts-pipeline/carousel-routine/output/2026-07-08/carousel-branded",
    "carousel_title": "Meta Muse Image Backlash",
    "caption": "Meta launched their new AI generator 'Muse Image' today, and users are furious over how their personal photos were used to train it.\n\nWe are entering the era of the 'Data Dividend.' Consumers are realizing their data is the fuel for trillion-dollar AI models, and they want a cut—or at least control.\n\nSwipe to see how this shift will fundamentally change how AI apps acquire data over the next 24 months.\n\n#DataPrivacy #ArtificialIntelligence #TechNews"
  },
  {
    "id": 2, "slot": "4:00 PM", "type": "image", "date": sched_date, "post_now": False,
    "image_png": "/Users/apple/Documents/{{BRAND_SHORT_NAME}}-data/daily-linkedin-posts-pipeline/linkedin-infographic-20260708.png",
    "caption": "Why isn't Open Source AI hurting Anthropic and OpenAI yet?\n\nBecause most businesses don't have the internal engineering talent to deploy, fine-tune, and secure open-source models like Llama 3 or Mistral on their own servers.\n\nBut that is changing. As deployment tools get easier, UAE enterprises will shift from expensive proprietary APIs to secure, self-hosted open-source models.\n\nThe cost difference is staggering.\n\nIs your business ready to run its own AI infrastructure?\n\n#EnterpriseAI #OpenSource #DubaiTech #{{BRAND_SHORT_NAME}}"
  }
]

posts_today = {
  "date": date_str,
  "schedule_date": sched_date,
  "generated_at": datetime.datetime.now().isoformat(),
  "ahmed_linkedin": {{AUTHOR_NAME_LOWER}}_posts,
  "{{BRAND_SHORT_NAME_LOWER}}_linkedin": eco_posts,
  "{{BRAND_SHORT_NAME_LOWER}}_instagram": []
}

with open("posts_today.json", "w") as f:
    json.dump(posts_today, f, indent=2)

print("Data generated for July 8!")
