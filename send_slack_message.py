import sys
import json
import urllib.request

if len(sys.argv) < 2:
    print("Usage: python send_slack_message.py 'Message text'")
    exit(1)

text = sys.argv[1]

# Read token from .env
slack_token = None
env_path = "/Users/apple/Documents/{{BRAND_SHORT_NAME}}-data/daily-linkedin-posts-pipeline/.env"
try:
    with open(env_path) as f:
        for line in f:
            if line.startswith("SLACK_BOT_TOKEN="):
                slack_token = line.strip().split("=", 1)[1]
                break
except Exception as e:
    exit(1)

channel = "C0BD1BYFK0D" # #all-{{BRAND_SHORT_NAME_LOWER}}-solution-slack

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
req = urllib.request.Request(
    url, 
    data=json.dumps(payload).encode("utf-8"), 
    headers=headers,
    method="POST"
)
try:
    with urllib.request.urlopen(req) as res:
        pass
except Exception as e:
    pass
