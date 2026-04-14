#!/usr/bin/env python3
import os
import json
import argparse
import hashlib


def url_to_filename(url):
    hash_obj = hashlib.md5(url.encode("utf-8"))
    return hash_obj.hexdigest()


def delete_story(url):
    print(f"Deleting story: {url}")

    # Generate filenames
    filename_hash = url_to_filename(url)
    html_filename = f"{filename_hash}.html"
    md_filename = f"{filename_hash}.md"

    # Paths
    html_path = os.path.join("stories", html_filename)
    md_path = os.path.join("website", "content", "stories", md_filename)

    # Delete HTML file
    if os.path.exists(html_path):
        os.remove(html_path)
        print(f"Deleted HTML file: {html_path}")
    else:
        print(f"HTML file not found: {html_path}")

    # Delete Markdown file
    if os.path.exists(md_path):
        os.remove(md_path)
        print(f"Deleted Markdown file: {md_path}")
    else:
        print(f"Markdown file not found: {md_path}")

    # Remove URL from story_urls.json
    urls_json_path = "story_urls.json"
    if os.path.exists(urls_json_path):
        with open(urls_json_path, "r") as f:
            try:
                urls = json.load(f)
            except json.JSONDecodeError:
                print(f"Error: Could not parse {urls_json_path}")
                return

        if isinstance(urls, list):
            if url in urls:
                urls.remove(url)
                with open(urls_json_path, "w") as f:
                    json.dump(urls, f, indent=2)
                print(f"Removed URL from {urls_json_path}")
            else:
                print(f"URL not found in {urls_json_path}")
        else:
            print(f"Error: {urls_json_path} does not contain a list")
    else:
        print(f"{urls_json_path} not found")

    print("Story deletion completed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Delete a single story from HTML, Markdown, and URLs JSON."
    )
    parser.add_argument("url", help="The URL of the story to delete")
    args = parser.parse_args()

    delete_story(args.url)
