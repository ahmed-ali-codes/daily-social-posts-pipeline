import os
import json
import urllib.request
import ssl
from datetime import datetime

with open(".env", "r") as f:
    env_vars = {}
    for line in f:
        if "=" in line:
            k, v = line.split("=", 1)
            env_vars[k.strip()] = v.strip()

slack_token = env_vars.get("SLACK_BOT_TOKEN", "")
channel = env_vars.get("SLACK_CHANNEL_ID", "C0BD1BYFK0D")

date_str = datetime.today().strftime('%Y-%m-%d')
pdf_path = f"./carousel-routine/output/{date_str}/carousel-branded/startup-strategy-carousel.pdf"

files_to_upload = [
    pdf_path,
    "./instagram-image-1.png",
    "./instagram-image-3.png",
    "./instagram-carousel-01.png",
    "./instagram-carousel-02.png",
    "./instagram-carousel-03.png",
    "./instagram-carousel-04.png",
    "./instagram-carousel-05.png"
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def upload_file(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    filename = os.path.basename(file_path)
    print(f"Uploading {filename}...")
    
    file_size = os.path.getsize(file_path)
    
    try:
        req = urllib.request.Request(
            f"https://slack.com/api/files.getUploadURLExternal?filename={filename}&length={file_size}",
            headers={"Authorization": f"Bearer {slack_token}"}
        )
        with urllib.request.urlopen(req, context=ctx) as response:
            res = json.loads(response.read())
            
        if not res.get("ok"):
            print(f"Error getting upload URL for {filename}: {res}")
            return
            
        upload_url = res["upload_url"]
        file_id = res["file_id"]
        
        with open(file_path, "rb") as f:
            file_data = f.read()
            
        req_up = urllib.request.Request(upload_url, data=file_data, method="POST")
        with urllib.request.urlopen(req_up, context=ctx) as response:
            pass
            
        complete_data = json.dumps({
            "files": [{"id": file_id, "title": filename}],
            "channel_id": channel,
            "initial_comment": f"Fresh design for {filename}"
        }).encode("utf-8")
        
        req_comp = urllib.request.Request(
            "https://slack.com/api/files.completeUploadExternal",
            data=complete_data,
            headers={
                "Authorization": f"Bearer {slack_token}",
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req_comp, context=ctx) as response:
            res_comp = json.loads(response.read())
            if res_comp.get("ok"):
                print(f"✓ Uploaded: {filename}")
            else:
                print(f"✗ Error completing upload: {res_comp}")
                
    except Exception as e:
        print(f"Upload failed for {filename}: {e}")

print(f"Sending fresh files to Slack channel {channel}...")
for f in files_to_upload:
    upload_file(f)
print("Done!")
