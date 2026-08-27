import os
import json
import urllib.request
import ssl

with open(".env", "r") as f:
    env_vars = {}
    for line in f:
        if "=" in line:
            k, v = line.split("=", 1)
            env_vars[k.strip()] = v.strip()

slack_token = env_vars.get("SLACK_BOT_TOKEN", "")
channel = env_vars.get("SLACK_CHANNEL_ID", "C0BD1BYFK0D")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

posts = [
  {
    "id": 1,
    "caption": "This one stat changes how Dubai businesses compete ⚡\n\nBusinesses that blog 11+ times a month get 3x more traffic 🤖\nMost UAE businesses are still doing this manually.\nThe ones that aren't? They're closing deals while their competitors are sleeping.\nAI automation isn't the future for Dubai's top SMBs. It's the present.\n\nFollow @{{BRAND_SHORT_NAME_LOWER}} for daily AI insights 👇\n\n#DubaiAI #UAEBusiness #AIAutomation #DubaiTech #GCCBusiness #WhatsAppAutomation #UAEStartups #DubaiFounders #{{BRAND_SHORT_NAME}}AI #BusinessAutomation",
    "images": ["instagram-image-1.png"]
  },
  {
    "id": 2,
    "caption": "AI Email Automation myths that cost Dubai businesses real money 💸\nSwipe to see what's actually true in 2026.\nSave this before your competitor figures it out ⬇\n\n#DubaiAI #UAEBusiness #AIAutomation #DubaiTech #GCCStartups #{{BRAND_SHORT_NAME}}AI #BusinessGrowth #UAEFounders",
    "images": [
      "instagram-carousel-01.png",
      "instagram-carousel-02.png",
      "instagram-carousel-03.png",
      "instagram-carousel-04.png",
      "instagram-carousel-05.png"
    ]
  },
  {
    "id": 3,
    "caption": "The gap between you and your competitor is closing every day they automate and you don't. 🔥\nUAE businesses that move fast on AI are already seeing the results.\nBook a free audit — link in bio.\n\n#DubaiAI #UAEBusiness #AIAutomation #DubaiEntrepreneur #GCCBusiness #{{BRAND_SHORT_NAME}}AI #DubaiStartups #BusinessGrowthUAE #AIAgency #DigitalDubai",
    "images": ["instagram-image-3.png"]
  }
]

def send_message(text):
    data = json.dumps({"channel": channel, "text": text}).encode("utf-8")
    req = urllib.request.Request("https://slack.com/api/chat.postMessage", data=data, headers={
        "Authorization": f"Bearer {slack_token}",
        "Content-Type": "application/json"
    })
    urllib.request.urlopen(req, context=ctx)

def upload_file(file_path, comment=None):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    filename = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    try:
        req = urllib.request.Request(f"https://slack.com/api/files.getUploadURLExternal?filename={filename}&length={file_size}", headers={"Authorization": f"Bearer {slack_token}"})
        with urllib.request.urlopen(req, context=ctx) as response:
            res = json.loads(response.read())
        if not res.get("ok"): return
        upload_url, file_id = res["upload_url"], res["file_id"]
        with open(file_path, "rb") as f: file_data = f.read()
        req_up = urllib.request.Request(upload_url, data=file_data, method="POST")
        urllib.request.urlopen(req_up, context=ctx)
        
        complete_data = {"files": [{"id": file_id, "title": filename}], "channel_id": channel}
        if comment: complete_data["initial_comment"] = comment
        
        req_comp = urllib.request.Request("https://slack.com/api/files.completeUploadExternal", data=json.dumps(complete_data).encode("utf-8"), headers={"Authorization": f"Bearer {slack_token}", "Content-Type": "application/json"})
        urllib.request.urlopen(req_comp, context=ctx)
        print(f"Uploaded {filename}")
    except Exception as e:
        print(f"Failed {filename}: {e}")

send_message("🚨 *MANUAL INSTAGRAM UPLOAD REQUIRED* 🚨\nHere are the images and captions for today's {{BRAND_SHORT_NAME}} Instagram posts.")

for post in posts:
    send_message(f"====================\n*POST {post['id']} CAPTION:*\n```\n{post['caption']}\n```\n_Images attaching below..._")
    for img in post['images']:
        upload_file(img)

print("All done!")
