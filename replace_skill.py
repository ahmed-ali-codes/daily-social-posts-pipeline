import re

with open('skills/branded-carousel/SKILL.md', 'r') as f:
    content = f.read()

new_content = """### SHARED DESIGN SYSTEM — MIDNIGHT MONOLITH & ACCENT COLOR ROTATION

This is a premium, high-contrast, editorial design system featuring massive typography, a dark #0B0B0C background with radial glows, and a single accent color for emphasis.

**COLOR PALETTE ROTATION:**
Instead of hardcoding a single brand color, you must **randomly select ONE color** from the curated premium palette below, OR use the featured product's official primary brand color (if it looks good on a dark background).

**Curated Premium Palette:**
- `Neon Cyan`: `#00E5FF`
- `Cyber Pink`: `#FF0055`
- `Electric Violet`: `#B92B27`
- `Neon Green`: `#00FF87`
- `Vercel Blue`: `#0070F3`
- `Notion Red`: `#E16259`
- `Anthropic Peach`: `#D4A574`

Select the color and use it as `{{BRAND_COLOR}}` in all CSS blocks below.

**Color palette (hardcoded background/text):**
```css
  background-color: #0B0B0C; /* deep dark background */
  color: #FFFFFF; /* white text */
```

**Google Fonts (include in every slide):**
```html
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Instrument+Serif:ital@1&display=swap" rel="stylesheet"/>
```

**Base layout/typography rules:**
1. **Typography Size:** The numbers (`90%`, `24/7`, `3s`) are HUGE (`160-200px`), with tight letter-spacing (`-8px`). Headlines are `65-85px`, tight letter-spacing (`-2px` to `-3px`). 
2. **Serif Italic Emphasis:** One or two key words in the headline must be wrapped in `<em>...</em>`, which styles it in the `Instrument Serif` italic font, colored in `{{BRAND_COLOR}}`, with `text-shadow: 0 0 20px {{BRAND_COLOR}}`.
3. **Pill Badges:** Slide numbers are housed in `44px` solid `rgba(255,255,255,0.1)` circles in the top right, with a 1px solid `rgba(255,255,255,0.2)` border and `backdrop-filter: blur(10px)`.

---

### TEMPLATE 1 — Hook Slide (slide-01.html)

**Layout:** Top header, huge central stat and headline, bottom left square image.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=1080"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Instrument+Serif:ital@1&display=swap" rel="stylesheet"/>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { width: 1080px; height: 1080px; overflow: hidden; background-color: #0B0B0C; color: #FFFFFF; font-family: 'Outfit', sans-serif; position: relative; }
  body::before { content: ""; position: absolute; top: -20%; left: -20%; width: 60%; height: 60%; background: radial-gradient(circle, {{BRAND_COLOR}}40 0%, transparent 70%); filter: blur(80px); z-index: 1; pointer-events: none; }
  
  .header { position: absolute; top: 60px; left: 70px; right: 70px; display: flex; justify-content: space-between; align-items: center; z-index: 10; }
  .header-left { display: flex; align-items: center; gap: 12px; font-size: 14px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #A0AABF; }
  .star-icon { width: 24px; height: 24px; filter: drop-shadow(0 0 10px {{BRAND_COLOR}}); }
  .header-right { display: flex; align-items: center; gap: 15px; }
  .fw-text { font-family: 'Instrument Serif', serif; font-style: italic; font-size: 26px; color: #64748B; }
  .slide-badge { width: 44px; height: 44px; background-color: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.15); backdrop-filter: blur(12px); border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-weight: 700; font-size: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }

  .content { position: absolute; top: 260px; left: 70px; right: 70px; z-index: 5; }
  .headline { font-size: 85px; font-weight: 800; letter-spacing: -2px; line-height: 1.1; text-shadow: 0 4px 20px rgba(0,0,0,0.5); }
  .headline em { font-family: 'Instrument Serif', serif; font-style: italic; color: {{BRAND_COLOR}}; font-weight: 400; letter-spacing: 0; padding-left: 5px; text-shadow: 0 0 25px {{BRAND_COLOR}}60; }

  .bottom-area { position: absolute; bottom: 70px; left: 70px; right: 70px; display: flex; justify-content: space-between; align-items: center; z-index: 5; }
  .s1-bottom { display: flex; gap: 40px; align-items: center; }
  .s1-image { width: 340px; height: 340px; object-fit: cover; border-radius: 24px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 20px 50px rgba(0,0,0,0.8); }
  .bottom-text { font-size: 24px; font-weight: 400; color: #A0AABF; line-height: 1.5; max-width: 480px; }
  .swipe { font-size: 14px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #A0AABF; }
</style>
</head>
<body>
  <div class="header">
    <div class="header-left">
      <svg class="star-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 0L13.5 10.5L24 12L13.5 13.5L12 24L10.5 13.5L0 12L10.5 10.5L12 0Z" fill="{{BRAND_COLOR}}"/><path d="M4.5 4.5L10.5 10.5M19.5 19.5L13.5 13.5M19.5 4.5L13.5 10.5M4.5 19.5L10.5 13.5" stroke="{{BRAND_COLOR}}" stroke-width="2"/></svg>
      {{HEADER_LABEL}}
    </div>
    <div class="header-right">
      <div class="fw-text">{{BRAND_SHORT_NAME_LOWER}} solutions / 2026</div>
      <div class="slide-badge">01</div>
    </div>
  </div>
  <div class="content">
    <div class="headline">{{HOOK_PART_1}}</div>
    <div class="headline" style="margin-top: -10px;">{{HOOK_PART_2}} <em>{{HOOK_EMPHASIS}}.</em></div>
  </div>
  <div class="bottom-area">
    <div class="s1-bottom">
      <img src="assets/hero-ui.png" class="s1-image" onerror="this.src='assets/interface.png'"/>
      <div class="bottom-text">{{SUBTITLE}}</div>
    </div>
    <div class="swipe">SWIPE &rarr;</div>
  </div>
</body>
</html>
```

---

### TEMPLATE 2 & 4 — Top Image Fade (slide-02.html, slide-04.html)

**Layout:** Large blurred/faded image at the top half. Bottom half holds an eyebrow, headline, and subhead. 

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=1080"/>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Instrument+Serif:ital@1&display=swap" rel="stylesheet"/>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { width: 1080px; height: 1080px; overflow: hidden; background-color: #0B0B0C; color: #FFFFFF; font-family: 'Outfit', sans-serif; position: relative; }
  
  .top-image-container { position: absolute; top: 0; left: 0; right: 0; height: 450px; z-index: 1; }
  .top-image { width: 100%; height: 100%; object-fit: cover; object-position: center 20%; filter: brightness(0.7) contrast(1.1); }
  .image-fade { position: absolute; bottom: -2px; left: 0; right: 0; height: 250px; background: linear-gradient(to bottom, transparent, #0B0B0C); }
  .top-image-container::after { content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(circle at 50% 100%, {{BRAND_COLOR}}30 0%, transparent 60%); pointer-events: none; }

  .pill-header { position: absolute; top: 60px; left: 70px; right: 70px; display: flex; justify-content: space-between; align-items: center; z-index: 10; }
  .pill-left { display: flex; align-items: center; gap: 12px; background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(20px); padding: 12px 24px; border-radius: 40px; color: #FFFFFF; font-size: 14px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
  .pill-badge { width: 44px; height: 44px; background-color: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(20px); border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-weight: 700; font-size: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }

  .content { position: absolute; top: 400px; left: 70px; right: 70px; z-index: 5; }
  .eyebrow { font-size: 18px; font-weight: 700; color: {{BRAND_COLOR}}; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 20px; text-shadow: 0 0 15px {{BRAND_COLOR}}80; }
  .headline.medium { font-size: 65px; font-weight: 800; letter-spacing: -2px; line-height: 1.1; text-shadow: 0 4px 20px rgba(0,0,0,0.8); }
  .headline.medium em { font-family: 'Instrument Serif', serif; font-style: italic; color: {{BRAND_COLOR}}; font-weight: 400; padding-left: 5px; text-shadow: 0 0 25px {{BRAND_COLOR}}60; }
  .subhead { font-size: 28px; font-weight: 400; color: #A0AABF; margin-top: 25px; line-height: 1.4; }

  .bottom-area { position: absolute; bottom: 70px; left: 70px; right: 70px; display: flex; justify-content: space-between; align-items: flex-end; z-index: 5; }
  .bottom-text { font-size: 24px; font-weight: 400; color: #E2E8F0; line-height: 1.5; max-width: 750px; background: rgba(0,0,0,0.3); padding: 20px 30px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.05); backdrop-filter: blur(10px); }
  .swipe { font-size: 14px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #A0AABF; padding-bottom: 20px; }
</style>
</head>
<body>
  <div class="top-image-container">
    <img src="assets/interface.png" class="top-image" onerror="this.style.display='none'"/>
    <div class="image-fade"></div>
  </div>
  <div class="pill-header">
    <div class="pill-left">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 0L13.5 10.5L24 12L13.5 13.5L12 24L10.5 13.5L0 12L10.5 10.5L12 0Z" fill="{{BRAND_COLOR}}"/><path d="M4.5 4.5L10.5 10.5M19.5 19.5L13.5 13.5M19.5 4.5L13.5 10.5M4.5 19.5L10.5 13.5" stroke="{{BRAND_COLOR}}" stroke-width="2"/></svg>
      {{PILL_LABEL}}
    </div>
    <div class="pill-badge">{{SLIDE_NUM}}</div>
  </div>
  <div class="content">
    <div class="eyebrow">{{EYEBROW}}</div>
    <div class="headline medium">{{HEADLINE_PART_1}}</div>
    <div class="headline medium">{{HEADLINE_PART_2}} <em>{{HEADLINE_EMPHASIS}}.</em></div>
    <div class="subhead">{{SUBHEAD}}</div>
  </div>
  <div class="bottom-area">
    <div class="bottom-text">{{BODY_TEXT}}</div>
    <div class="swipe">SWIPE &rarr;</div>
  </div>
</body>
</html>
```

---

### TEMPLATE 3 & 5 — Data Circle (slide-03.html, slide-05.html)

**Layout:** No image. Standard header. Left side features a huge glowing number (`24/7` or `3s`). Right side of the number sits a thick brand-colored circle with mini context text inside.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=1080"/>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Instrument+Serif:ital@1&display=swap" rel="stylesheet"/>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { width: 1080px; height: 1080px; overflow: hidden; background-color: #0B0B0C; color: #FFFFFF; font-family: 'Outfit', sans-serif; position: relative; }
  body::before { content: ""; position: absolute; top: 10%; right: 10%; width: 50%; height: 50%; background: radial-gradient(circle, {{BRAND_COLOR}}25 0%, transparent 70%); filter: blur(80px); z-index: 1; pointer-events: none; }
  
  .header { position: absolute; top: 60px; left: 70px; right: 70px; display: flex; justify-content: space-between; align-items: center; z-index: 10; }
  .header-left { display: flex; align-items: center; gap: 12px; font-size: 14px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #A0AABF; }
  .header-right { display: flex; align-items: center; gap: 15px; }
  .fw-text { font-family: 'Instrument Serif', serif; font-style: italic; font-size: 26px; color: #64748B; }
  .slide-badge { width: 44px; height: 44px; background-color: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.15); backdrop-filter: blur(12px); border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-weight: 700; font-size: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }

  .content { position: absolute; top: 300px; left: 70px; right: 70px; z-index: 5; }
  .huge-number { font-size: 200px; font-weight: 800; letter-spacing: -6px; line-height: 0.9; margin-bottom: 10px; display: inline-block; text-shadow: 0 0 40px rgba(255,255,255,0.2); }
  
  .badge-container { display: inline-flex; align-items: center; justify-content: center; vertical-align: top; margin-left: 30px; margin-top: 15px; position: relative; }
  .badge-container::after { content: ""; position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); width: 100%; height: 100%; border-radius: 50%; box-shadow: 0 0 50px {{BRAND_COLOR}}60; z-index: -1; }
  .thick-circle { width: 150px; height: 150px; border: 4px solid {{BRAND_COLOR}}; background: rgba(0,0,0,0.5); backdrop-filter: blur(10px); border-radius: 50%; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: inset 0 0 20px {{BRAND_COLOR}}40; }
  .circle-text { font-size: 22px; font-weight: 800; line-height: 1; letter-spacing: 1px; color: #FFFFFF; }
  .circle-sub { font-family: 'Instrument Serif', serif; font-style: italic; font-size: 24px; color: {{BRAND_COLOR}}; margin-top: 4px; }
  
  .headline.medium { font-size: 65px; font-weight: 800; letter-spacing: -2px; line-height: 1.1; }
  .headline.medium em { font-family: 'Instrument Serif', serif; font-style: italic; color: {{BRAND_COLOR}}; font-weight: 400; padding-left: 5px; text-shadow: 0 0 25px {{BRAND_COLOR}}60; }

  .bottom-area { position: absolute; bottom: 70px; left: 70px; right: 70px; display: flex; justify-content: space-between; align-items: flex-end; z-index: 5; }
  .bottom-text { font-size: 24px; font-weight: 400; color: #A0AABF; line-height: 1.5; max-width: 750px; }
  .swipe { font-size: 14px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #A0AABF; }
</style>
</head>
<body>
  <div class="header">
    <div class="header-left">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0 0 10px {{BRAND_COLOR}});"><path d="M12 0L13.5 10.5L24 12L13.5 13.5L12 24L10.5 13.5L0 12L10.5 10.5L12 0Z" fill="{{BRAND_COLOR}}"/><path d="M4.5 4.5L10.5 10.5M19.5 19.5L13.5 13.5M19.5 4.5L13.5 10.5M4.5 19.5L10.5 13.5" stroke="{{BRAND_COLOR}}" stroke-width="2"/></svg>
      {{HEADER_LABEL}}
    </div>
    <div class="header-right">
      <div class="fw-text">{{BRAND_SHORT_NAME_LOWER}} solutions / 2026</div>
      <div class="slide-badge">{{SLIDE_NUM}}</div>
    </div>
  </div>
  <div class="content">
    <div>
      <div class="huge-number">{{HUGE_STAT}}</div>
      <div class="badge-container">
        <div class="thick-circle">
          <div class="circle-text">{{CIRCLE_WORD_1}}</div>
          <div class="circle-sub">{{CIRCLE_WORD_2}}</div>
        </div>
      </div>
    </div>
    <div class="headline medium" style="margin-top: 30px;">{{HEADLINE_PART_1}}</div>
    <div class="headline medium">{{HEADLINE_PART_2}} <em>{{HEADLINE_EMPHASIS}}.</em></div>
  </div>
  <div class="bottom-area">
    <div class="bottom-text">{{BODY_TEXT}}</div>
    <div class="swipe">SWIPE &rarr;</div>
  </div>
</body>
</html>
```

---

### TEMPLATE 6 — Results (slide-06.html)

**Layout:** Two column. Left is huge number + headline. Right is a square product screenshot floating in glass.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=1080"/>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Instrument+Serif:ital@1&display=swap" rel="stylesheet"/>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { width: 1080px; height: 1080px; overflow: hidden; background-color: #0B0B0C; color: #FFFFFF; font-family: 'Outfit', sans-serif; position: relative; }
  body::before { content: ""; position: absolute; bottom: -20%; right: -20%; width: 60%; height: 60%; background: radial-gradient(circle, {{BRAND_COLOR}}30 0%, transparent 70%); filter: blur(80px); z-index: 1; pointer-events: none; }
  
  .header { position: absolute; top: 60px; left: 70px; right: 70px; display: flex; justify-content: space-between; align-items: center; z-index: 10; }
  .header-left { display: flex; align-items: center; gap: 12px; font-size: 14px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #A0AABF; }
  .header-right { display: flex; align-items: center; gap: 15px; }
  .fw-text { font-family: 'Instrument Serif', serif; font-style: italic; font-size: 26px; color: #64748B; }
  .slide-badge { width: 44px; height: 44px; background-color: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.15); backdrop-filter: blur(12px); border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-weight: 700; font-size: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }

  .content { position: absolute; top: 220px; left: 70px; right: 70px; z-index: 5; }
  .s6-container { display: flex; justify-content: space-between; align-items: center; margin-top: 50px; }
  .s6-left { flex: 1; padding-right: 40px; }
  
  .huge-number { font-size: 140px; font-weight: 800; letter-spacing: -4px; line-height: 1; margin-bottom: 20px; text-shadow: 0 0 30px rgba(255,255,255,0.2); }
  .headline.medium { font-size: 55px; font-weight: 800; letter-spacing: -1.5px; line-height: 1.15; }
  .headline.medium em { font-family: 'Instrument Serif', serif; font-style: italic; color: {{BRAND_COLOR}}; font-weight: 400; padding-left: 5px; text-shadow: 0 0 20px {{BRAND_COLOR}}60; }
  .subhead { font-size: 24px; font-weight: 400; color: #A0AABF; margin-top: 20px; line-height: 1.4; }

  .s6-image-wrapper { position: relative; padding: 20px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); backdrop-filter: blur(20px); border-radius: 40px; box-shadow: 0 30px 60px rgba(0,0,0,0.8); }
  .s6-image { width: 380px; height: 380px; object-fit: cover; border-radius: 24px; }
  
  .bottom-area { position: absolute; bottom: 70px; left: 70px; right: 70px; display: flex; justify-content: space-between; align-items: flex-end; z-index: 5; }
  .bottom-text { font-size: 24px; font-weight: 400; color: #A0AABF; line-height: 1.5; max-width: 750px; }
  .swipe { font-size: 14px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #A0AABF; }
</style>
</head>
<body>
  <div class="header">
    <div class="header-left">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0 0 10px {{BRAND_COLOR}});"><path d="M12 0L13.5 10.5L24 12L13.5 13.5L12 24L10.5 13.5L0 12L10.5 10.5L12 0Z" fill="{{BRAND_COLOR}}"/><path d="M4.5 4.5L10.5 10.5M19.5 19.5L13.5 13.5M19.5 4.5L13.5 10.5M4.5 19.5L10.5 13.5" stroke="{{BRAND_COLOR}}" stroke-width="2"/></svg>
      {{HEADER_LABEL}}
    </div>
    <div class="header-right">
      <div class="fw-text">{{BRAND_SHORT_NAME_LOWER}} solutions / 2026</div>
      <div class="slide-badge">06</div>
    </div>
  </div>
  <div class="content">
    <div class="s6-container">
      <div class="s6-left">
        <div class="huge-number">{{HUGE_STAT}}</div>
        <div class="headline medium">{{HEADLINE_PART_1}}</div>
        <div class="headline medium">{{HEADLINE_PART_2}} <em>{{HEADLINE_EMPHASIS}}.</em></div>
        <div class="subhead">{{SUBHEAD}}</div>
      </div>
      <div class="s6-image-wrapper">
        <img src="assets/hero-ui.png" class="s6-image" onerror="this.src='assets/interface.png'"/>
      </div>
    </div>
  </div>
  <div class="bottom-area">
    <div class="bottom-text">{{BODY_TEXT}}</div>
    <div class="swipe">SWIPE &rarr;</div>
  </div>
</body>
</html>
```

---

### TEMPLATE 7 — The Lesson / CTA (slide-07.html)

**Layout:** No image. Large text center, glowing divider line, and a neon pill button at the bottom.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=1080"/>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Instrument+Serif:ital@1&display=swap" rel="stylesheet"/>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { width: 1080px; height: 1080px; overflow: hidden; background-color: #0B0B0C; color: #FFFFFF; font-family: 'Outfit', sans-serif; position: relative; }
  body::before { content: ""; position: absolute; bottom: -30%; left: 50%; transform: translateX(-50%); width: 80%; height: 60%; background: radial-gradient(circle, {{BRAND_COLOR}}20 0%, transparent 60%); filter: blur(100px); z-index: 1; pointer-events: none; }
  
  .header { position: absolute; top: 60px; left: 70px; right: 70px; display: flex; justify-content: space-between; align-items: center; z-index: 10; }
  .header-left { display: flex; align-items: center; gap: 12px; font-size: 14px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #A0AABF; }
  .header-right { display: flex; align-items: center; gap: 15px; }
  .fw-text { font-family: 'Instrument Serif', serif; font-style: italic; font-size: 26px; color: #64748B; }
  .slide-badge { width: 44px; height: 44px; background-color: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.15); backdrop-filter: blur(12px); border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-weight: 700; font-size: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }

  .content { position: absolute; top: 280px; left: 70px; right: 70px; z-index: 5; text-align: center; display: flex; flex-direction: column; align-items: center; }
  .headline { font-size: 85px; font-weight: 800; letter-spacing: -2px; line-height: 1.1; text-shadow: 0 4px 20px rgba(0,0,0,0.5); }
  .headline em { font-family: 'Instrument Serif', serif; font-style: italic; color: {{BRAND_COLOR}}; font-weight: 400; padding-left: 5px; text-shadow: 0 0 30px {{BRAND_COLOR}}80; }
  
  .s7-line { width: 100px; height: 4px; background: {{BRAND_COLOR}}; margin: 50px auto; border-radius: 2px; box-shadow: 0 0 20px {{BRAND_COLOR}}; }
  .subhead { font-size: 32px; font-weight: 400; color: #A0AABF; max-width: 900px; line-height: 1.4; }

  .bottom-area { position: absolute; bottom: 80px; left: 0; right: 0; display: flex; justify-content: center; z-index: 5; }
  .s7-pill { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 20px 40px rgba(0,0,0,0.5), inset 0 0 20px rgba(255,255,255,0.05); backdrop-filter: blur(20px); color: white; padding: 24px 48px; border-radius: 100px; font-size: 22px; font-weight: 600; display: inline-flex; align-items: center; letter-spacing: 0.5px; }
  .s7-pill em { font-family: 'Instrument Serif', serif; font-style: italic; color: {{BRAND_COLOR}}; font-weight: 400; margin-left: 8px; font-size: 28px; text-shadow: 0 0 15px {{BRAND_COLOR}}80; }
</style>
</head>
<body>
  <div class="header">
    <div class="header-left">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0 0 10px {{BRAND_COLOR}});"><path d="M12 0L13.5 10.5L24 12L13.5 13.5L12 24L10.5 13.5L0 12L10.5 10.5L12 0Z" fill="{{BRAND_COLOR}}"/><path d="M4.5 4.5L10.5 10.5M19.5 19.5L13.5 13.5M19.5 4.5L13.5 10.5M4.5 19.5L10.5 13.5" stroke="{{BRAND_COLOR}}" stroke-width="2"/></svg>
      THE LESSON
    </div>
    <div class="header-right">
      <div class="fw-text">{{BRAND_SHORT_NAME_LOWER}} solutions / 2026</div>
      <div class="slide-badge">07</div>
    </div>
  </div>
  <div class="content">
    <div class="headline">{{HEADLINE_PART_1}}</div>
    <div class="headline">{{HEADLINE_PART_2}} <em>{{HEADLINE_EMPHASIS}}.</em></div>
    <div class="s7-line"></div>
    <div class="subhead">{{SUBHEAD}}</div>
  </div>
  <div class="bottom-area">
    <div class="s7-pill">follow {{BRAND_SHORT_NAME_LOWER}} solutions for daily <em>frameworks.</em></div>
  </div>
</body>
</html>
```"""

import re
content_new = re.sub(
    r"### SHARED DESIGN SYSTEM — CREAM & ACCENT COLOR ROTATION.*?## PHASE 4 — Render PNGs",
    new_content + "\n\n## PHASE 4 — Render PNGs",
    content,
    flags=re.DOTALL
)

with open('skills/branded-carousel/SKILL.md', 'w') as f:
    f.write(content_new)

print("Replaced design system successfully!")
