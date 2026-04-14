import requests
import os
import json
import time
import hashlib

def url_to_filename(url):
    hash_obj = hashlib.md5(url.encode('utf-8'))
    return hash_obj.hexdigest()

with open("story_urls.json", "r") as f:
    urls = json.load(f)

# Download only first 3 stories for testing
test_urls = urls[:3]

stories_dir = "stories"
os.makedirs(stories_dir, exist_ok=True)

for i, url in enumerate(test_urls, 1):
    filename = url_to_filename(url) + ".html"
    filepath = os.path.join(stories_dir, filename)
    
    print(f"[{i}/{len(test_urls)}] Downloading {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(filepath, "wb") as f:
            f.write(response.content)
        
        print(f"  Saved to {filename}")
        time.sleep(0.5)
    except Exception as e:
        print(f"  Error: {e}")

print(f"\nDownloaded {len(test_urls)} stories to {stories_dir}/")
