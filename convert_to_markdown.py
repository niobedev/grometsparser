import os
import re
import yaml
from datetime import datetime
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import glob
import argparse
import hashlib
import json


def url_to_filename(url):
    hash_obj = hashlib.md5(url.encode("utf-8"))
    return hash_obj.hexdigest()


def parse_story_html(html, url, site_mapping=None):
    soup = BeautifulSoup(html, "html.parser")

    metadata = {}
    metadata["original_url"] = url

    if site_mapping and url in site_mapping:
        metadata["subcategory"] = site_mapping[url]

    plaza_header = soup.find(string=re.compile(r"Gromet's\s+Plaza"))
    if plaza_header:
        parent = plaza_header.find_parent()
        if parent:
            text = parent.get_text()
            match = re.search(r"Plaza\s*(\w+\s*\w*)", text)
            if match:
                subcategory = match.group(1).strip()
                if subcategory and subcategory != "Plaza":
                    if "subcategory" not in metadata:
                        metadata["subcategory"] = subcategory

    title = soup.find("h1")
    if title:
        metadata["title"] = title.get_text(strip=True)

    author_elem = soup.find("h3", id="author")
    if author_elem:
        author_link = author_elem.find("a")
        if author_link:
            metadata["authors"] = [author_link.get_text(strip=True)]
        else:
            metadata["authors"] = [
                author_elem.get_text(strip=True).replace("by ", "").strip()
            ]

    storycodes_div = soup.find("div", id="forum")
    if storycodes_div and "Storycodes:" in storycodes_div.get_text():
        storycodes_text = storycodes_div.get_text(strip=True)
        match = re.search(r"Storycodes:\s*(.+)", storycodes_text)
        if match:
            codes = match.group(1)
            tags = [
                tag.strip().replace("/", "-") for tag in codes.split(";") if tag.strip()
            ]
            metadata["tags"] = tags

    content_div = soup.find("div", id="main", class_="storym")
    if not content_div:
        content_div = soup.find("div", class_="storym")
    if content_div:
        import copy

        content_copy = copy.copy(content_div)

        for br in content_copy.find_all("br"):
            br.replace_with("\n")

        content_html = str(content_copy)

        date_elem = content_div.find_next_sibling("p")
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            date_match = re.search(r"(\d{2})\.(\d{2})\.(\d{2,4})", date_text)
            if date_match:
                day = date_match.group(1)
                month = date_match.group(2)
                year = date_match.group(3)
                if len(year) == 2:
                    year_full = "20" + year if int(year) < 50 else "19" + year
                else:
                    year_full = year
                metadata["date"] = datetime(int(year_full), int(month), int(day))
    else:
        content_html = ""

    story_markdown = md(content_html, heading_style="ATX")

    story_markdown = re.sub(
        r"(\n|^)[\*_]*(\s*)\*\*Author\'s Note:?\*\*\s*",
        r"\1_**Author\'s Note:** _",
        story_markdown,
    )
    story_markdown = re.sub(
        r"\*\*\*([^*]+)\*\*(.+?)\*", r"_**\1**\2_", story_markdown, flags=re.DOTALL
    )
    story_markdown = re.sub(r"[ \t]+$", "", story_markdown, flags=re.MULTILINE)

    def fix_italics(match):
        content = match.group(1)
        content = content.strip()
        if "\n\n" in content:
            paragraphs = content.split("\n\n")
            return "\n\n".join([f"_{p.strip()}_" for p in paragraphs if p.strip()])
        return f"_{content}_"

    story_markdown = re.sub(r"_(.+?)_", fix_italics, story_markdown, flags=re.DOTALL)
    story_markdown = re.sub(r"\|[\s\|-]*\n", "", story_markdown)
    story_markdown = re.sub(r"\n{3,}", "\n\n", story_markdown)
    story_markdown = re.sub(r"[ \t]+$", "", story_markdown, flags=re.MULTILINE)
    story_markdown = story_markdown.strip()

    date_match = re.search(r"(\d{2})\.(\d{2})\.(\d{2,4})\s*$", story_markdown)
    if date_match:
        day = int(date_match.group(1))
        month = int(date_match.group(2))
        year = date_match.group(3)
        if 1 <= day <= 31 and 1 <= month <= 12:
            if len(year) == 2:
                year_full = "20" + year if int(year) < 50 else "19" + year
            else:
                year_full = year
            date_obj = datetime(int(year_full), month, day)
            metadata["date"] = date_obj
            story_markdown = re.sub(
                r"\n*\d{2}\.\d{2}\.\d{2,4}\s*$", "", story_markdown
            ).strip()

    story_markdown = re.sub(
        r"You can also.*?Plaza Forum.*?(?:<\/a>)?\s*",
        "",
        story_markdown,
        flags=re.DOTALL,
    ).strip()

    story_markdown = re.sub(r"\]\(#forum\)", "", story_markdown).strip()

    return metadata, story_markdown


def convert_all_stories(force=False):
    source_dir = "stories"
    target_dir = "website/content/stories"
    os.makedirs(target_dir, exist_ok=True)

    url_map = {}
    if os.path.exists("story_urls.json"):
        with open("story_urls.json", "r") as f:
            urls = json.load(f)
            for u in urls:
                filename = url_to_filename(u) + ".html"
                url_map[filename] = u

    site_mapping = {}
    if os.path.exists("story_site_mapping.json"):
        with open("story_site_mapping.json", "r") as f:
            site_mapping = json.load(f)

    html_files = glob.glob(os.path.join(source_dir, "*.html"))

    # Filter out already converted files unless force=True
    files_to_convert = []
    for filepath in html_files:
        filename = os.path.basename(filepath)
        hash_name = filename.replace(".html", "")
        target_path = os.path.join(target_dir, hash_name + ".md")

        if force or not os.path.exists(target_path):
            files_to_convert.append(filepath)

    print(
        f"Converting {len(files_to_convert)} HTML stories to Markdown (out of {len(html_files)} total)..."
    )

    for i, filepath in enumerate(files_to_convert, 1):
        filename = os.path.basename(filepath)
        hash_name = filename.replace(".html", "")
        target_path = os.path.join(target_dir, hash_name + ".md")

        print(
            f"[{i}/{len(files_to_convert)}] Converting {filename}...",
            end="\r",
            flush=True,
        )

        try:
            with open(filepath, "rb") as f:
                raw_html = f.read()

            from bs4 import UnicodeDammit

            dammit = UnicodeDammit(raw_html, is_html=True)
            encoding = dammit.original_encoding

            if encoding and encoding.lower() in ["iso-8859-1", "latin-1"]:
                encoding = "cp1252"

            try:
                html_text = raw_html.decode(
                    encoding or "utf-8", errors="replace"
                ).replace("\x00", "")
            except (UnicodeDecodeError, LookupError):
                html_text = raw_html.decode("utf-8", errors="replace").replace(
                    "\x00", ""
                )

            url = url_map.get(filename, f"https://grometsplaza.net/")
            metadata, content = parse_story_html(html_text, url, site_mapping)

            if "title" not in metadata:
                metadata["title"] = "Untitled"

            yaml_header = yaml.dump(metadata, sort_keys=False, allow_unicode=True)

            with open(target_path, "w", encoding="utf-8") as f:
                f.write("---\n")
                f.write(yaml_header)
                f.write("---\n\n")
                f.write(content)
                f.write("\n")

        except Exception as e:
            print(f"\nError converting {filename}: {e}")

    print(f"\nFinished converting {len(html_files)} stories.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert HTML stories to Markdown.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force conversion of all stories, even if already converted.",
    )
    args = parser.parse_args()

    convert_all_stories(force=args.force)
