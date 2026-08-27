import os
import json

out_dir = "./carousel-routine/temp/carousel-branded"
os.makedirs(out_dir, exist_ok=True)

# Colors and fonts
bg_color = "#0A0F1A"
text_color = "#FFFFFF"
accent_color = "#00D4FF"
sub_color = "#94A3B8"
font_family = "'Space Grotesk', sans-serif"

# Load data
json_data = {}
if os.path.exists("./carousel_data.json"):
    try:
        with open("./carousel_data.json") as f:
            json_data = json.load(f)
    except Exception as e:
        print(f"Error loading carousel_data.json: {e}")

def get_slide_val(slide_num, key, fallback=""):
    slide_obj = json_data.get(str(slide_num), json_data.get(slide_num, {}))
    return slide_obj.get(key, fallback)

base_css = f"""
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ width: 1080px; height: 1080px; overflow: hidden; background-color: {bg_color}; color: {text_color}; font-family: {font_family}; position: relative; }}
  
  .header {{ position: absolute; top: 60px; left: 70px; right: 70px; display: flex; justify-content: space-between; align-items: center; z-index: 10; }}
  .header-left {{ display: flex; align-items: center; gap: 15px; font-size: 16px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; color: {accent_color}; }}
  .header-right {{ display: flex; align-items: center; gap: 15px; }}
  .fw-text {{ font-size: 22px; color: {sub_color}; font-weight: 500; letter-spacing: 1px; }}
  .slide-badge {{ width: 50px; height: 50px; border: 2px solid {accent_color}; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: {accent_color}; font-weight: 700; font-size: 18px; box-shadow: 0 0 15px rgba(0, 212, 255, 0.3); }}
  
  .bottom-area {{ position: absolute; bottom: 70px; left: 70px; right: 70px; display: flex; justify-content: space-between; align-items: flex-end; z-index: 5; }}
  .swipe {{ font-size: 16px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; color: {accent_color}; }}
  .glow {{ text-shadow: 0 0 20px rgba(0, 212, 255, 0.5); }}
"""

def generate_slide_1():
    h1 = get_slide_val(1, "HOOK_PART_1")
    h2 = get_slide_val(1, "HOOK_PART_2")
    hem = get_slide_val(1, "HOOK_EMPHASIS")
    sub = get_slide_val(1, "SUBTITLE")
    header = get_slide_val(1, "HEADER_LABEL")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=1080"/>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700;900&display=swap" rel="stylesheet"/>
<style>
{base_css}
  .content {{ position: absolute; top: 300px; left: 70px; right: 70px; z-index: 5; }}
  .headline {{ font-size: 90px; font-weight: 900; letter-spacing: -2px; line-height: 1.1; }}
  .headline span {{ color: {accent_color}; text-shadow: 0 0 30px rgba(0, 212, 255, 0.6); }}
  .bottom-text {{ font-size: 32px; font-weight: 400; color: {sub_color}; line-height: 1.5; max-width: 800px; }}
  .hero-glass {{ position: absolute; top: 50%; right: -100px; width: 600px; height: 600px; background: radial-gradient(circle, rgba(0,212,255,0.15) 0%, rgba(10,15,26,0) 70%); transform: translateY(-50%); z-index: 1; }}
</style>
</head>
<body>
  <div class="hero-glass"></div>
  <div class="header">
    <div class="header-left">{header}</div>
    <div class="header-right">
      <div class="fw-text">{{BRAND_SHORT_NAME_LOWER}} solutions / 2026</div>
      <div class="slide-badge">01</div>
    </div>
  </div>
  <div class="content">
    <div class="headline">{h1}</div>
    <div class="headline">{h2.replace(hem, f"<span>{hem}</span>")}</div>
  </div>
  <div class="bottom-area">
    <div class="bottom-text">{sub}</div>
    <div class="swipe glow">SWIPE &rarr;</div>
  </div>
</body>
</html>"""
    return html

def generate_slide_2_4(num):
    eyebrow = get_slide_val(num, "EYEBROW")
    h1 = get_slide_val(num, "HEADLINE_PART_1")
    h2 = get_slide_val(num, "HEADLINE_PART_2")
    hem = get_slide_val(num, "HEADLINE_EMPHASIS")
    sub = get_slide_val(num, "SUBHEAD")
    body = get_slide_val(num, "BODY_TEXT")
    label = get_slide_val(num, "PILL_LABEL")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=1080"/>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700;900&display=swap" rel="stylesheet"/>
<style>
{base_css}
  .content {{ position: absolute; top: 350px; left: 70px; right: 70px; z-index: 5; }}
  .eyebrow {{ font-size: 22px; font-weight: 700; color: {accent_color}; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 25px; }}
  .headline {{ font-size: 70px; font-weight: 900; letter-spacing: -2px; line-height: 1.1; }}
  .headline span {{ color: {accent_color}; }}
  .subhead {{ font-size: 36px; font-weight: 700; color: #E2E8F0; margin-top: 30px; line-height: 1.4; border-left: 4px solid {accent_color}; padding-left: 20px; }}
  .bottom-text {{ font-size: 28px; font-weight: 400; color: {sub_color}; line-height: 1.5; max-width: 800px; }}
</style>
</head>
<body>
  <div class="header">
    <div class="header-left">{label}</div>
    <div class="header-right">
      <div class="fw-text">{{BRAND_SHORT_NAME_LOWER}} solutions / 2026</div>
      <div class="slide-badge">0{num}</div>
    </div>
  </div>
  <div class="content">
    <div class="eyebrow">{eyebrow}</div>
    <div class="headline">{h1}</div>
    <div class="headline">{h2.replace(hem, f"<span>{hem}</span>")}</div>
    <div class="subhead">{sub}</div>
  </div>
  <div class="bottom-area">
    <div class="bottom-text">{body}</div>
    <div class="swipe glow">SWIPE &rarr;</div>
  </div>
</body>
</html>"""
    return html

def generate_slide_3_5(num):
    stat = get_slide_val(num, "HUGE_STAT")
    c1 = get_slide_val(num, "CIRCLE_WORD_1")
    c2 = get_slide_val(num, "CIRCLE_WORD_2")
    h1 = get_slide_val(num, "HEADLINE_PART_1")
    h2 = get_slide_val(num, "HEADLINE_PART_2")
    hem = get_slide_val(num, "HEADLINE_EMPHASIS")
    body = get_slide_val(num, "BODY_TEXT")
    label = get_slide_val(num, "HEADER_LABEL")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=1080"/>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700;900&display=swap" rel="stylesheet"/>
<style>
{base_css}
  .content {{ position: absolute; top: 250px; left: 70px; right: 70px; z-index: 5; }}
  .huge-number {{ font-size: 220px; font-weight: 900; letter-spacing: -10px; line-height: 0.9; margin-bottom: 30px; display: inline-block; color: transparent; -webkit-text-stroke: 2px {accent_color}; }}
  .circle-group {{ display: inline-flex; align-items: center; justify-content: center; vertical-align: top; margin-left: 30px; margin-top: 20px; }}
  .circle {{ width: 180px; height: 180px; background: rgba(0,212,255,0.1); border: 2px solid {accent_color}; border-radius: 50%; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: inset 0 0 20px rgba(0,212,255,0.2), 0 0 30px rgba(0,212,255,0.2); }}
  .c-text1 {{ font-size: 26px; font-weight: 900; color: #FFF; text-transform: uppercase; }}
  .c-text2 {{ font-size: 24px; font-weight: 500; color: {accent_color}; text-transform: uppercase; }}
  .headline {{ font-size: 70px; font-weight: 900; letter-spacing: -2px; line-height: 1.1; }}
  .headline span {{ color: {accent_color}; }}
  .bottom-text {{ font-size: 28px; font-weight: 400; color: {sub_color}; line-height: 1.5; max-width: 800px; }}
</style>
</head>
<body>
  <div class="header">
    <div class="header-left">{label}</div>
    <div class="header-right">
      <div class="fw-text">{{BRAND_SHORT_NAME_LOWER}} solutions / 2026</div>
      <div class="slide-badge">0{num}</div>
    </div>
  </div>
  <div class="content">
    <div>
      <div class="huge-number">{stat}</div>
      <div class="circle-group">
        <div class="circle">
          <div class="c-text1">{c1}</div>
          <div class="c-text2">{c2}</div>
        </div>
      </div>
    </div>
    <div class="headline" style="margin-top:20px;">{h1}</div>
    <div class="headline">{h2.replace(hem, f"<span>{hem}</span>")}</div>
  </div>
  <div class="bottom-area">
    <div class="bottom-text">{body}</div>
    <div class="swipe glow">SWIPE &rarr;</div>
  </div>
</body>
</html>"""
    return html

def generate_slide_6():
    stat = get_slide_val(6, "HUGE_STAT")
    h1 = get_slide_val(6, "HEADLINE_PART_1")
    h2 = get_slide_val(6, "HEADLINE_PART_2")
    hem = get_slide_val(6, "HEADLINE_EMPHASIS")
    sub = get_slide_val(6, "SUBHEAD")
    body = get_slide_val(6, "BODY_TEXT")
    label = get_slide_val(6, "HEADER_LABEL")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=1080"/>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700;900&display=swap" rel="stylesheet"/>
<style>
{base_css}
  .content {{ position: absolute; top: 220px; left: 70px; right: 70px; z-index: 5; }}
  .stat-block {{ font-size: 140px; font-weight: 900; color: {accent_color}; line-height: 1; margin-bottom: 20px; text-shadow: 0 0 40px rgba(0,212,255,0.4); }}
  .headline {{ font-size: 70px; font-weight: 900; letter-spacing: -2px; line-height: 1.1; }}
  .headline span {{ border-bottom: 4px solid {accent_color}; }}
  .subhead {{ font-size: 34px; font-weight: 700; color: #FFF; margin-top: 30px; line-height: 1.4; }}
  .bottom-text {{ font-size: 28px; font-weight: 400; color: {sub_color}; line-height: 1.5; max-width: 800px; }}
</style>
</head>
<body>
  <div class="header">
    <div class="header-left">{label}</div>
    <div class="header-right">
      <div class="fw-text">{{BRAND_SHORT_NAME_LOWER}} solutions / 2026</div>
      <div class="slide-badge">06</div>
    </div>
  </div>
  <div class="content">
    <div class="stat-block">{stat}</div>
    <div class="headline">{h1}</div>
    <div class="headline">{h2.replace(hem, f"<span>{hem}</span>")}</div>
    <div class="subhead">{sub}</div>
  </div>
  <div class="bottom-area">
    <div class="bottom-text">{body}</div>
    <div class="swipe glow">SWIPE &rarr;</div>
  </div>
</body>
</html>"""
    return html

def generate_slide_7():
    h1 = get_slide_val(7, "HEADLINE_PART_1")
    h2 = get_slide_val(7, "HEADLINE_PART_2")
    hem = get_slide_val(7, "HEADLINE_EMPHASIS")
    sub = get_slide_val(7, "SUBHEAD")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=1080"/>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700;900&display=swap" rel="stylesheet"/>
<style>
{base_css}
  body {{ background: radial-gradient(circle at center, #111A2E 0%, #0A0F1A 100%); }}
  .content {{ position: absolute; top: 400px; left: 70px; right: 70px; z-index: 5; text-align: center; }}
  .headline {{ font-size: 80px; font-weight: 900; letter-spacing: -2px; line-height: 1.1; }}
  .headline span {{ color: {accent_color}; text-shadow: 0 0 30px rgba(0, 212, 255, 0.6); }}
  .subhead {{ font-size: 32px; font-weight: 500; color: {sub_color}; margin-top: 40px; line-height: 1.5; }}
  .cta-button {{ display: inline-block; margin-top: 50px; padding: 20px 40px; background: {accent_color}; color: #0A0F1A; font-size: 24px; font-weight: 900; text-transform: uppercase; border-radius: 10px; box-shadow: 0 10px 30px rgba(0, 212, 255, 0.4); }}
</style>
</head>
<body>
  <div class="content">
    <div class="headline">{h1}</div>
    <div class="headline">{h2.replace(hem, f"<span>{hem}</span>")}</div>
    <div class="subhead">{sub}</div>
    <div class="cta-button">Follow @ahmedali</div>
  </div>
</body>
</html>"""
    return html

slides = {
    1: generate_slide_1(),
    2: generate_slide_2_4(2),
    3: generate_slide_3_5(3),
    4: generate_slide_2_4(4),
    5: generate_slide_3_5(5),
    6: generate_slide_6(),
    7: generate_slide_7(),
}

for num, html in slides.items():
    with open(f"{out_dir}/slide-0{num}.html", "w") as f:
        f.write(html)
        
print("Successfully generated dark theme HTML slides.")
