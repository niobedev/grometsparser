#!/usr/bin/env python3
import json
import os
import re
import sys
from datetime import datetime

import yaml


def main():
    site_url = os.environ.get("SITE_URL", "https://plaza.housetoral.uk")
    stories_file = "new_stories_info.json"
    output_file = "matrix_message.json"

    if not os.path.exists(stories_file):
        print("No new_stories_info.json found, skipping")
        sys.exit(1)

    with open(stories_file) as f:
        stories = json.load(f)

    max_show = 5
    shown = stories[:max_show]
    remaining = len(stories) - max_show

    plain_lines = []
    html_lines = []

    for i, story in enumerate(shown, 1):
        title = story["title"]
        slug = story["slug"]
        md_path = f"website/content/stories/{slug}.md"
        link = None

        if os.path.exists(md_path):
            with open(md_path) as f:
                content = f.read()
            fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            if fm_match:
                fm = yaml.safe_load(fm_match.group(1))
                date_val = fm.get("date")
                if date_val:
                    if isinstance(date_val, datetime):
                        d = date_val
                    else:
                        d = datetime.strptime(str(date_val).split()[0], "%Y-%m-%d")
                    link = f"{site_url}/stories/{d.year}/{d.month:02d}/{d.day:02d}/{slug}/"

        plain_lines.append(f"{i}) {title}")
        if link:
            html_lines.append(f'{i}) <a href="{link}">{title}</a>')
        else:
            html_lines.append(f"{i}) {title}")

    plain_body = "\U0001f195 New stories added on Plaza!\n\n" + "\n".join(plain_lines)
    html_body = "<b>\U0001f195 New stories added on Plaza!</b><br><br>" + "<br>".join(html_lines)

    if remaining > 0:
        plain_body += f"\n\nand {remaining} more"
        html_body += f"<br><br>and {remaining} more"

    plain_body += f"\n\nView at: {site_url}"
    html_body += f'<br><br>View at: <a href="{site_url}">{site_url}</a>'

    payload = {
        "msgtype": "m.text",
        "body": plain_body,
        "format": "org.matrix.custom.html",
        "formatted_body": html_body,
    }

    with open(output_file, "w") as f:
        json.dump(payload, f)

    print(f"Matrix message formatted: {len(stories)} stories, {len(shown)} shown")


if __name__ == "__main__":
    main()
