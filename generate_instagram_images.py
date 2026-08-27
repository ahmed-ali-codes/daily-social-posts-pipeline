import json
import re
import os

with open("posts_today.json", "r") as f:
    data = json.load(f)

ig_posts = data.get("{{BRAND_SHORT_NAME_LOWER}}_instagram", [])

for post in ig_posts:
    slot = post.get("slot", "")
    raw = post.get("raw", "")
    post_id = post.get("id", 1)
    
    if post.get("type") == "image":
        if post_id == 1:
            stat_match = re.search(r'CAPTION:\n(.*?)\n', raw)
            stat = stat_match.group(1) if stat_match else "AI Automation for Dubai Businesses"
            
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=1080"/>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700;900&family=Inter:wght@400;600&display=swap" rel="stylesheet"/>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ width: 1080px; height: 1080px; overflow: hidden; background-color: #0A0A0F; color: #FFFFFF; font-family: 'Space Grotesk', sans-serif; position: relative; display: flex; flex-direction: column; justify-content: center; align-items: center; }}
  
  .glow-bg {{ position: absolute; width: 800px; height: 800px; background: radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, rgba(10, 10, 15, 0) 70%); top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 1; }}
  
  .top-brand {{ position: absolute; top: 80px; display: flex; align-items: center; gap: 10px; font-family: 'Inter', sans-serif; font-weight: 600; font-size: 18px; letter-spacing: 4px; color: #94A3B8; text-transform: uppercase; z-index: 5; }}
  .icon {{ color: #3B82F6; font-size: 24px; }}
  
  .content {{ position: relative; z-index: 5; text-align: center; max-width: 900px; padding: 0 40px; }}
  .stat {{ font-size: 55px; font-weight: 900; line-height: 1.3; letter-spacing: -1px; }}
  
  .bottom-brand {{ position: absolute; bottom: 80px; font-family: 'Inter', sans-serif; font-size: 18px; color: #64748B; font-weight: 400; letter-spacing: 1px; z-index: 5; display: flex; flex-direction: column; align-items: center; gap: 15px; }}
  .schedule {{ color: #3B82F6; font-weight: 600; font-size: 16px; background: rgba(59, 130, 246, 0.1); padding: 8px 16px; border-radius: 20px; }}
</style>
</head>
<body>
  <div class="glow-bg"></div>
  <div class="top-brand"><span class="icon">✦</span> ECOTRUSTIA SOLUTIONS</div>
  
  <div class="content">
    <div class="stat">{stat}</div>
  </div>
  
  <div class="bottom-brand">
    <div>@{{BRAND_SHORT_NAME_LOWER}} | Dubai AI Agency</div>
    <div class="schedule">Scheduled for: {slot}</div>
  </div>
</body>
</html>"""
            with open(f"./instagram-image-{post_id}.html", "w") as out:
                out.write(html)
                
        elif post_id == 3:
            headline = "Your competitors aren't waiting."
            subline = "Neither should you."
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=1080"/>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700;900&family=Inter:wght@400;600&display=swap" rel="stylesheet"/>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ width: 1080px; height: 1080px; overflow: hidden; background-color: #0A0A0F; color: #FFFFFF; font-family: 'Space Grotesk', sans-serif; position: relative; display: flex; flex-direction: column; justify-content: center; align-items: center; }}
  
  .glow-bg {{ position: absolute; width: 900px; height: 900px; background: radial-gradient(circle at bottom left, rgba(139, 92, 246, 0.15) 0%, rgba(10, 10, 15, 0) 70%); bottom: 0; left: 0; z-index: 1; }}
  
  .top-brand {{ position: absolute; top: 80px; font-family: 'Inter', sans-serif; font-weight: 600; font-size: 18px; letter-spacing: 4px; color: #94A3B8; text-transform: uppercase; z-index: 5; }}
  
  .content {{ position: relative; z-index: 5; text-align: center; max-width: 900px; }}
  .headline {{ font-size: 85px; font-weight: 900; line-height: 1.1; letter-spacing: -2px; margin-bottom: 20px; }}
  .subline {{ font-size: 70px; font-weight: 900; color: #3B82F6; text-shadow: 0 0 30px rgba(59, 130, 246, 0.4); }}
  
  .bottom-brand {{ position: absolute; bottom: 80px; font-family: 'Inter', sans-serif; font-size: 18px; color: #64748B; font-weight: 400; letter-spacing: 1px; z-index: 5; display: flex; flex-direction: column; align-items: center; gap: 15px; }}
  .schedule {{ color: #3B82F6; font-weight: 600; font-size: 16px; background: rgba(59, 130, 246, 0.1); padding: 8px 16px; border-radius: 20px; }}
</style>
</head>
<body>
  <div class="glow-bg"></div>
  <div class="top-brand">ECOTRUSTIA SOLUTIONS</div>
  
  <div class="content">
    <div class="headline">{headline}</div>
    <div class="subline">{subline}</div>
  </div>
  
  <div class="bottom-brand">
    <div>@{{BRAND_SHORT_NAME_LOWER}} | Dubai AI Agency</div>
    <div class="schedule">Scheduled for: {slot}</div>
  </div>
</body>
</html>"""
            with open(f"./instagram-image-{post_id}.html", "w") as out:
                out.write(html)
                
    elif post.get("type") == "carousel":
        slides = []
        hook_match = re.search(r'SLIDE 1 — HOOK:\nHeadline: (.*?)\nSubtext: (.*?)\n', raw)
        if hook_match:
            slides.append({"hook": hook_match.group(1).strip(), "sub": hook_match.group(2).strip()})
            
        for i in range(2, 5):
            slide_match = re.search(rf'SLIDE {i}:\nHeadline: (.*?)\n(?:Body: )?(?:Reality: )?(.*?)\n', raw)
            if slide_match:
                slides.append({"myth": slide_match.group(1).strip(), "reality": slide_match.group(2).strip()})
                
        cta_match = re.search(r'SLIDE 5 — CTA:\nHeadline: (.*?)\nCTA Text: (.*?)\nHandle: (.*?)$', raw)
        if cta_match:
            slides.append({"cta": cta_match.group(1).strip(), "sub_cta": cta_match.group(2).strip(), "handle": cta_match.group(3).strip()})
        
        if len(slides) < 5:
            slides = [
                {"hook": "AI Automated Call Service sounds expensive and complicated", "sub": "Most Dubai SMBs think that. Here's the truth."},
                {"myth": "Myth: You need a big team to implement AI", "reality": "A single automation setup handles what 2 full-time staff used to do."},
                {"myth": "Myth: It takes months to see results", "reality": "The fastest-moving Dubai clients see measurable improvement within the first week."},
                {"myth": "Myth: It's only for large corporations", "reality": "Our clients range from solo consultants to 20-person teams."},
                {"cta": "Ready to see what your business could automate?", "sub_cta": "Book a free audit — DM us \\\"AUDIT\\\"", "handle": "@{{BRAND_SHORT_NAME_LOWER}}"}
            ]
        
        base_css = """
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { width: 1080px; height: 1080px; overflow: hidden; background-color: #0A0A0F; color: #FFFFFF; font-family: 'Space Grotesk', sans-serif; position: relative; }
  .glow-bg { position: absolute; width: 1000px; height: 1000px; background: radial-gradient(circle at top right, rgba(59, 130, 246, 0.15) 0%, rgba(10, 10, 15, 0) 70%); top: -200px; right: -200px; z-index: 1; }
  .card { position: absolute; top: 150px; bottom: 150px; left: 100px; right: 100px; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 40px; backdrop-filter: blur(20px); z-index: 5; padding: 80px; display: flex; flex-direction: column; justify-content: center; }
  .swipe { position: absolute; bottom: 60px; right: 100px; font-size: 16px; font-weight: 700; letter-spacing: 3px; color: #3B82F6; z-index: 10; text-shadow: 0 0 10px rgba(59, 130, 246, 0.5); display: flex; flex-direction: column; align-items: flex-end; gap: 15px; }
  .schedule { color: #94A3B8; font-size: 14px; letter-spacing: 1px; background: rgba(59, 130, 246, 0.1); padding: 8px 16px; border-radius: 20px; color: #3B82F6; text-shadow: none; font-weight: 600; letter-spacing: 0px; }
"""
        
        for i, slide in enumerate(slides):
            if i == 0:
                content = f"""
                <div style="font-size: 60px; font-weight: 900; line-height: 1.1; margin-bottom: 40px; letter-spacing: -2px;">{slide['hook'].replace('AI Automated Call Service', '<span style="color:#3B82F6;text-shadow:0 0 20px rgba(59,130,246,0.4)">AI Automated Call Service</span>')}</div>
                <div style="font-size: 32px; color: #94A3B8; line-height: 1.5; font-weight: 500;">{slide['sub']}</div>
                """
            elif i == 4:
                content = f"""
                <div style="text-align: center;">
                    <div style="font-size: 70px; font-weight: 900; line-height: 1.1; margin-bottom: 50px; letter-spacing: -2px;">{slide['cta']}</div>
                    <div style="display: inline-block; background: #3B82F6; color: #0A0A0F; padding: 25px 50px; border-radius: 15px; font-size: 28px; font-weight: 900; margin-bottom: 40px; box-shadow: 0 10px 30px rgba(59,130,246,0.3);">{slide['sub_cta']}</div>
                    <div style="font-size: 28px; color: #94A3B8; font-family: 'Inter', sans-serif;">{slide['handle']}</div>
                </div>
                """
            else:
                content = f"""
                <div style="background: rgba(239, 68, 68, 0.1); color: #EF4444; padding: 10px 20px; border-radius: 8px; display: inline-block; font-weight: 700; font-size: 20px; letter-spacing: 2px; margin-bottom: 30px; text-transform: uppercase;">Myth</div>
                <div style="font-size: 45px; font-weight: 900; line-height: 1.2; margin-bottom: 50px; letter-spacing: -1px;">{slide['myth'].replace('Myth: ', '')}</div>
                <div style="background: rgba(59, 130, 246, 0.1); color: #3B82F6; padding: 10px 20px; border-radius: 8px; display: inline-block; font-weight: 700; font-size: 20px; letter-spacing: 2px; margin-bottom: 30px; text-transform: uppercase;">Reality</div>
                <div style="font-size: 30px; color: #E2E8F0; line-height: 1.5; font-weight: 500;">{slide['reality'].replace('Reality: ', '')}</div>
                """
                
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=1080"/>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700;900&family=Inter:wght@400;500;700&display=swap" rel="stylesheet"/>
<style>{base_css}</style>
</head>
<body>
  <div class="glow-bg"></div>
  <div class="card">
    {content}
  </div>
  <div class="swipe">
    { '<div>SWIPE &rarr;</div>' if i < 4 else '' }
    <div class="schedule">Scheduled for: {slot}</div>
  </div>
</body>
</html>"""
            with open(f"./instagram-carousel-0{i+1}.html", "w") as out:
                out.write(html)
print("Generated Instagram HTML files successfully.")
