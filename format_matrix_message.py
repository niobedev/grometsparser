#!/usr/bin/env python3
import json
import os
import sys


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

        plain_lines.append(f"- {title}")
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
