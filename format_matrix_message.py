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

    plain_lines = []
    html_items = []

    for story in stories:
        title = story["title"]
        file_id = story["slug"]
        md_path = f"website/content/stories/{file_id}.md"
        link = None

        if os.path.exists(md_path):
            with open(md_path) as f:
                content = f.read()
            fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            if fm_match:
                fm = yaml.safe_load(fm_match.group(1))
                slug_val = fm.get("slug", file_id)
                date_val = fm.get("date")
                if date_val:
                    if isinstance(date_val, datetime):
                        d = date_val
                    else:
                        d = datetime.strptime(str(date_val).split()[0], "%Y-%m-%d")
                    link = f"{site_url}/stories/{d.year}/{d.month:02d}/{d.day:02d}/{slug_val}/"

        plain_lines.append(f"- {title}")
        if link:
            html_items.append(f'<li><a href="{link}">{title}</a></li>')
        else:
            html_items.append(f"<li>{title}</li>")

    plain_body = "\U0001f195 New stories were published on Plaza!\n\n" + "\n".join(plain_lines)
    html_body = "<b>\U0001f195 New stories were published on Plaza!</b><br><br><ul>" + "".join(html_items) + "</ul>"

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

    print(f"Matrix message formatted: {len(stories)} stories")


if __name__ == "__main__":
    main()
