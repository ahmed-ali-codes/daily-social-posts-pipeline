import os

out_dir = "./carousel-routine/temp/carousel-branded"
os.makedirs(out_dir, exist_ok=True)

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=1080"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet"/>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { 
    width: 1080px; height: 1350px; overflow: hidden; 
    background-color: #050505; color: #FFFFFF; 
    font-family: 'Inter', sans-serif; position: relative; 
  }
  
  /* Noise Texture */
  body::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background-image: url('data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noiseFilter%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.85%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noiseFilter)%22/%3E%3C/svg%3E');
    opacity: 0.04; z-index: 1; pointer-events: none;
  }
  
  /* Gradient Orbs */
  .orb-1 {
    position: absolute; top: -10%; left: -10%; width: 800px; height: 800px;
    background: radial-gradient(circle, #00E5FF 0%, transparent 70%);
    filter: blur(120px); opacity: 0.15; z-index: 0;
  }
  .orb-2 {
    position: absolute; bottom: -10%; right: -10%; width: 900px; height: 900px;
    background: radial-gradient(circle, #FF0055 0%, transparent 70%);
    filter: blur(150px); opacity: 0.12; z-index: 0;
  }

  /* Glass Card */
  .glass-card {
    position: absolute; top: 120px; bottom: 180px; left: 60px; right: 60px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    backdrop-filter: blur(30px);
    border-radius: 40px;
    padding: 80px 60px;
    z-index: 5;
    box-shadow: 0 30px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1);
    display: flex; flex-direction: column; justify-content: center;
  }
  
  .eyebrow {
    font-size: 24px; font-weight: 700; text-transform: uppercase; letter-spacing: 4px;
    background: linear-gradient(90deg, #00E5FF, #7C3AED);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 30px;
  }
  
  .headline {
    font-size: 72px; font-weight: 800; letter-spacing: -2px; line-height: 1.1; margin-bottom: 40px;
  }
  
  .body-text {
    font-size: 36px; font-weight: 400; color: #A1A1AA; line-height: 1.5; max-width: 800px;
  }

  /* Progress Bar */
  .progress-container {
    position: absolute; top: 60px; left: 60px; right: 60px;
    display: flex; gap: 8px; z-index: 10;
  }
  .progress-dash {
    height: 4px; flex: 1; border-radius: 2px;
    background: rgba(255,255,255,0.1);
  }
  .progress-dash.active { background: #00E5FF; box-shadow: 0 0 10px #00E5FF; }
  .progress-dash.done { background: rgba(255,255,255,0.4); }

  /* Footer Profile */
  .footer {
    position: absolute; bottom: 60px; left: 60px; right: 60px;
    display: flex; justify-content: space-between; align-items: center; z-index: 10;
  }
  .profile { display: flex; align-items: center; gap: 20px; }
  .avatar { width: 64px; height: 64px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.2); background: #fff; }
  .name { font-size: 24px; font-weight: 700; }
  .handle { font-size: 18px; color: #71717A; }
  .swipe { font-size: 20px; font-weight: 600; letter-spacing: 2px; color: #A1A1AA; text-transform: uppercase; }
</style>
</head>
<body>
  <div class="orb-1"></div>
  <div class="orb-2"></div>
  
  <div class="progress-container">
    {{PROGRESS_BARS}}
  </div>

  <div class="glass-card" style="{{CARD_STYLE}}">
    <div class="eyebrow">{{EYEBROW}}</div>
    <div class="headline">{{HEADLINE}}</div>
    <div class="body-text">{{BODY_TEXT}}</div>
  </div>

  <div class="footer">
    <div class="profile">
      <div class="avatar">
        <!-- SVG Logo for {{BRAND_SHORT_NAME}} -->
        <svg viewBox="0 0 100 100" style="width:100%; height:100%; padding:10px;"><path d="M50 10 L90 90 L10 90 Z" fill="#00E5FF"/></svg>
      </div>
      <div>
        <div class="name">{{BRAND_NAME}}</div>
        <div class="handle">@{{BRAND_SHORT_NAME_LOWER}}</div>
      </div>
    </div>
    <div class="swipe">{{FOOTER_RIGHT}}</div>
  </div>
</body>
</html>
"""

slides_data = [
    {
        "eyebrow": "DATA OWNERSHIP",
        "headline": "The era of free<br><span style='color:#00E5FF'>training data</span> is over.",
        "body_text": "Meta launched 'Muse Image' today and users are furious about their photos being used.<br><br>Here is why the tech industry is about to face a massive data reckoning.",
        "card_style": "text-align: center; align-items: center;"
    },
    {
        "eyebrow": "THE PROBLEM",
        "headline": "Users are realizing their data is the product.",
        "body_text": "For years, users traded data for free services. But training a trillion-dollar generative AI model on personal photos feels like a massive overreach to the average consumer.<br><br>The implicit contract is broken.",
        "card_style": ""
    },
    {
        "eyebrow": "THE SHIFT",
        "headline": "Opt-out is no longer enough.",
        "body_text": "Burying a data scraping clause in a 40-page Terms of Service agreement is causing PR nightmares.<br><br>Regulators are stepping in, demanding explicit opt-in consent for AI training.",
        "card_style": ""
    },
    {
        "eyebrow": "THE SOLUTION",
        "headline": "Companies will have to start paying.",
        "body_text": "High quality data isn't free anymore.<br><br>In the next 24 months, we will see platforms emerge that actually compensate users for licensing their data to train foundation models.",
        "card_style": ""
    },
    {
        "eyebrow": "THE IMPACT",
        "headline": "Training costs will skyrocket.",
        "body_text": "When you can no longer scrape the entire internet for free, only the most well-funded giants will be able to afford the licensing fees for clean, legally-cleared training data.",
        "card_style": ""
    },
    {
        "eyebrow": "THE LESSON",
        "headline": "Build proprietary data flywheels.",
        "body_text": "If you are building an AI product, design loops where users willingly provide specific, high-intent data in exchange for immediate value, rather than scraping.",
        "card_style": ""
    },
    {
        "eyebrow": "THE VERDICT",
        "headline": "The free lunch<br>is <span style='color:#FF0055'>over.</span>",
        "body_text": "Prepare for the massive shift from data scraping to data licensing.<br><br>Are you building your own data moat?",
        "card_style": "text-align: center; align-items: center; border-color: rgba(255,0,85,0.3); box-shadow: 0 0 100px rgba(255,0,85,0.1);"
    }
]

total_slides = len(slides_data)

for i, slide in enumerate(slides_data):
    # Generate progress bars
    progress_html = ""
    for p in range(total_slides):
        if p < i:
            progress_html += "<div class='progress-dash done'></div>"
        elif p == i:
            progress_html += "<div class='progress-dash active'></div>"
        else:
            progress_html += "<div class='progress-dash'></div>"
            
    html = html_template
    html = html.replace("{{PROGRESS_BARS}}", progress_html)
    html = html.replace("{{EYEBROW}}", slide["eyebrow"])
    html = html.replace("{{HEADLINE}}", slide["headline"])
    html = html.replace("{{BODY_TEXT}}", slide["body_text"])
    html = html.replace("{{CARD_STYLE}}", slide["card_style"])
    
    footer_right = "SWIPE &rarr;" if i < total_slides - 1 else "FOLLOW FOR MORE"
    html = html.replace("{{FOOTER_RIGHT}}", footer_right)
    
    filename = f"{out_dir}/slide-0{i+1}.html"
    with open(filename, "w") as f:
        f.write(html)

print("Generated 7 elegant slides successfully in temp/carousel-branded.")
