#!/usr/bin/env python3
import os
import re
import sys
import json
import subprocess
import hashlib
import glob
from datetime import datetime
from bs4 import BeautifulSoup
import requests


def url_to_filename(url):
    hash_obj = hashlib.md5(url.encode("utf-8"))
    return hash_obj.hexdigest()


def get_title_from_html(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        title_elem = soup.find("h1")
        if title_elem:
            return title_elem.get_text(strip=True)
    except Exception:
        pass
    return None


def run_command(cmd, cwd=None):
    result = subprocess.run(
        cmd,
        cwd=cwd,
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def main():
    print("=" * 60)
    print("Gromet's Plaza Story Sync")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    stories_dir = "stories"
    os.makedirs(stories_dir, exist_ok=True)

    existing_html = set()
    for f in glob.glob(os.path.join(stories_dir, "*.html")):
        existing_html.add(os.path.basename(f))

    print("\n[1/4] Extracting story URLs...")
    venv_python = sys.executable
    rc, stdout, stderr = run_command(f"{venv_python} extract_urls.py")
    if rc != 0:
        print(f"Failed to extract URLs: {stderr}")
        sys.exit(1)

    if not os.path.exists("story_urls.json"):
        print("story_urls.json not created")
        sys.exit(1)

    with open("story_urls.json", "r") as f:
        urls = json.load(f)

    url_to_file = {url_to_filename(url) + ".html": url for url in urls}

    new_files = []
    for filename in existing_html:
        if filename not in url_to_file:
            continue
        url = url_to_file[filename]
        new_title = get_title_from_html(os.path.join(stories_dir, filename))
        if new_title:
            new_files.append((filename, new_title))

    if new_files:
        print(f"\n[2/4] {len(new_files)} new stories to process")

    print("\n[3/4] Downloading new stories...")
    venv_python = sys.executable
    rc, stdout, stderr = run_command(f"{venv_python} download_stories.py")
    if rc != 0:
        print(f"Failed to download stories: {stderr}")

    downloaded_files = []
    for f in glob.glob(os.path.join(stories_dir, "*.html")):
        filename = os.path.basename(f)
        if filename not in existing_html:
            url = url_to_file.get(filename)
            if url:
                title = get_title_from_html(f)
                if not title:
                    title = url
                downloaded_files.append((filename, title))

    if not downloaded_files:
        print("\nNo new stories downloaded.")
        print("Checking for updates to existing stories...")

    print("\n[4/4] Converting stories to markdown...")
    venv_python = sys.executable
    rc, stdout, stderr = run_command(f"{venv_python} convert_to_markdown.py")
    if rc != 0:
        print(f"Failed to convert stories: {stderr}")

    all_new_stories = downloaded_files

    all_new_stories.sort(key=lambda x: x[0])

    if all_new_stories:
        story_list = ", ".join([title for _, title in all_new_stories[:5]])
        if len(all_new_stories) > 5:
            story_list += f" and {len(all_new_stories) - 5} more"

        commit_msg = f"Add new stories: {story_list}"

        print(f"\nCommitting changes: {commit_msg}")

        rc, stdout, stderr = run_command("git add stories/ website/content/stories/")
        if rc != 0:
            print(f"git add failed: {stderr}")

        rc, stdout, stderr = run_command(f'git commit -m "{commit_msg}"')
        if rc != 0:
            if "nothing to commit" in stderr:
                print("No changes to commit.")
            else:
                print(f"git commit failed: {stderr}")
        else:
            print("Changes committed.")

            print("\nPushing to origin...")
            rc, stdout, stderr = run_command("git push origin main")
            if rc != 0:
                print(f"git push failed: {stderr}")
            else:
                print("Pushed to origin.")
    else:
        print("\nNo new stories to commit.")

    print("\n" + "=" * 60)
    print("Sync completed successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()
