#!/usr/bin/env python3
import requests
import json
import hashlib
import os
import sys
import subprocess
from datetime import datetime
from bs4 import BeautifulSoup


def url_to_filename(url):
    """Convert URL to filename using the same method as download_stories.py"""
    hash_obj = hashlib.md5(url.encode("utf-8"))
    return hash_obj.hexdigest()


def get_existing_stories():
    """Get set of existing story filenames"""
    stories_dir = "stories"
    existing = set()

    if os.path.exists(stories_dir):
        for filename in os.listdir(stories_dir):
            if filename.endswith(".html"):
                existing.add(filename)

    return existing


def extract_updates_from_main_page():
    """Extract story URLs from the Updates section on main.html"""
    print("Fetching main page...")

    try:
        response = requests.get("https://grometsplaza.net/main.html")
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching main page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # Find the updates section
    updates_dl = soup.find("dl", {"class": "updates"})
    if not updates_dl:
        print("Could not find updates section on main page")
        return []

    stories = []

    # Extract all story links from the updates section
    for a_tag in updates_dl.find_all("a", {"class": "newstory"}):
        href = a_tag.get("href")
        if not href:
            continue

        # Skip if it's not a story URL
        if not (href.endswith(".html") or "/stories/" in href):
            continue

        # Get story details
        title_span = a_tag.find("span", {"class": "title"})
        author_span = a_tag.find("span", {"class": "author"})
        site_span = a_tag.find("span", {"class": "site"})

        title = title_span.get_text(strip=True) if title_span else "Unknown"
        author = author_span.get_text(strip=True) if author_span else "Unknown"
        site = site_span.get_text(strip=True) if site_span else "Unknown"

        # Normalize URL
        if href.startswith("/"):
            href = "https://grometsplaza.net" + href
        elif not href.startswith("http"):
            href = "https://grometsplaza.net/" + href

        stories.append({"url": href, "title": title, "author": author, "site": site})

    return stories


def add_new_urls_to_file(new_stories):
    """Add new story URLs to story_urls.json (avoiding duplicates)"""
    new_urls = [story["url"] for story in new_stories]

    # Load existing URLs if file exists
    existing_urls = []
    if os.path.exists("story_urls.json"):
        try:
            with open("story_urls.json", "r") as f:
                existing_urls = json.load(f)
        except Exception as e:
            print(f"Warning: Could not read existing story_urls.json: {e}")

    # Combine and deduplicate
    all_urls = existing_urls + [url for url in new_urls if url not in existing_urls]

    # Write back
    with open("story_urls.json", "w") as f:
        json.dump(all_urls, f, indent=2)

    print(f"Updated story_urls.json with {len(new_urls)} new URLs")


def run_command(cmd, cwd=None):
    """Run a shell command and return result"""
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
    print("Gromet's Plaza Quick Sync - Updates Section")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Get existing stories
    existing_stories = get_existing_stories()
    print(f"Found {len(existing_stories)} existing stories")

    # Extract updates from main page
    updates = extract_updates_from_main_page()
    if not updates:
        print("No updates found or error fetching updates")
        return

    print(f"Found {len(updates)} stories in updates section")

    # Filter out existing stories
    new_stories = []
    for story in updates:
        filename = url_to_filename(story["url"]) + ".html"
        if filename not in existing_stories:
            new_stories.append(story)

    if not new_stories:
        print("No new stories found in updates section")
        return

    print(f"Found {len(new_stories)} new stories to download")

    # Show new stories
    print("\nNew stories:")
    for story in new_stories:
        print(f"  - {story['title']} by {story['author']} ({story['site']})")

    # Add new URLs to story_urls.json
    add_new_urls_to_file(new_stories)

    # Download the new stories using existing download_stories.py
    print("\nDownloading new stories...")
    venv_python = sys.executable
    rc, stdout, stderr = run_command(f"{venv_python} download_stories.py")

    if rc != 0:
        print(f"Error downloading stories: {stderr}")
        return

    # Convert to markdown using existing convert_to_markdown.py
    print("\nConverting to markdown...")
    rc, stdout, stderr = run_command(f"{venv_python} convert_to_markdown.py")

    if rc != 0:
        print(f"Error converting to markdown: {stderr}")

    # Commit changes if any
    print("\nCommitting changes...")
    rc, stdout, stderr = run_command(
        "git add stories/ website/content/stories/ story_urls.json"
    )

    if rc == 0:
        story_list = ", ".join([story["title"] for story in new_stories[:3]])
        if len(new_stories) > 3:
            story_list += f" and {len(new_stories) - 3} more"

        commit_msg = f"Quick sync: Add new stories from updates - {story_list}"

        rc, stdout, stderr = run_command(f'git commit -m "{commit_msg}"')

        if rc == 0:
            print("Changes committed.")

            print("Pushing to origin...")
            rc, stdout, stderr = run_command("git push origin main")

            if rc == 0:
                print("Pushed to origin.")
            else:
                print(f"Warning: git push failed: {stderr}")
        elif "nothing to commit" in stderr:
            print("No changes to commit.")
        else:
            print(f"Warning: git commit failed: {stderr}")
    else:
        print(f"Warning: git add failed: {stderr}")

    print("\n" + "=" * 60)
    print("Quick sync completed successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()
