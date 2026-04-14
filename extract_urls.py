import requests
from bs4 import BeautifulSoup
import json
import time
import re

BASE_URL = "https://grometsplaza.net/search.html"


def get_site_name(site_num):
    site_names = {
        1: "Selfbound Stories",
        2: "Mummified",
        3: "Bound Stories",
        4: "Latex Stories",
        5: "Packaged/Encasement",
        6: "Doll Stories",
        7: "Maid-bot Stories",
        8: "Spandex",
        9: "Erotic Stories",
        10: "Halloween Specials",
        11: "Trashcan Stories",
        12: "Devoured Stories",
        13: "Buried & Sinking",
        14: "Machine",
        15: "Transformation",
        16: "Giantess & Shrinking",
        17: "TG/CD Stories",
        18: "Pony & Pet Girl",
        19: "Other Worlds",
    }
    return site_names.get(site_num, f"Site {site_num}")


def get_story_urls_from_site(site_num):
    base_url = f"{BASE_URL}?site={site_num}"
    ajax_url = "https://grometsplaza.net/search_ajax.php"
    print(f"Fetching site {site_num}: {base_url}")

    response = requests.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    story_links = []

    expected_count = None
    found_count_text = soup.find(string=re.compile(r"\d+,?\d*\s+Stories Found"))
    if found_count_text:
        match = re.search(r"(\d+,?\d*)\s+Stories Found", found_count_text)
        if match:
            expected_count = int(match.group(1).replace(",", ""))
            print(f"  Expected stories: {expected_count}")

    nstart = 0
    while True:
        if nstart > 0:
            ajax_params = {"site": site_num, "nstart": nstart}
            print(f"  Fetching nstart={nstart}...")
            try:
                response = requests.get(ajax_url, params=ajax_params)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
            except Exception as e:
                print(f"    Error at nstart {nstart}: {e}")
                break

        content = (
            soup.find("div", {"id": "main"})
            or soup.find("div", {"class": "content"})
            or soup
        )

        page_links = []
        for a in content.find_all("a", href=True):
            href = a.get("href")

            if (
                not href
                or href.startswith("#")
                or href.startswith("mailto:")
                or href.startswith("javascript:")
            ):
                continue

            if any(
                skip in href
                for skip in [
                    "author_",
                    "main.html",
                    "search.html",
                    "pages/",
                    "forum",
                    "rss",
                    "storycodes",
                    "writers",
                    "links",
                    "legal",
                    "privacy",
                ]
            ):
                continue

            if "/stories" in href or (
                href.endswith(".html")
                and "author_" not in href
                and "main" not in href
                and "search" not in href
                and "storycodes" not in href
            ):
                if href.startswith("/"):
                    full_url = "https://grometsplaza.net" + href
                elif href.startswith("http"):
                    full_url = href
                else:
                    full_url = "https://grometsplaza.net/" + href

                if "stories" in full_url.lower() or full_url.endswith(".html"):
                    page_links.append(full_url)

        if not page_links:
            break

        story_links.extend(page_links)

        if expected_count and nstart + len(page_links) >= expected_count:
            break

        nstart += 100
        time.sleep(0.3)

    unique_links = list(set(story_links))

    if expected_count:
        print(f"  Found {len(unique_links)} stories (expected: {expected_count})")
    else:
        print(f"  Found {len(unique_links)} stories")

    return unique_links, expected_count


def main():
    all_story_urls = {}
    site_stats = {}

    for site_num in range(1, 20):
        try:
            links, expected = get_story_urls_from_site(site_num)
            site_name = get_site_name(site_num)

            for link in links:
                if link not in all_story_urls:
                    all_story_urls[link] = site_name
                else:
                    if all_story_urls[link] and site_name not in all_story_urls[link]:
                        all_story_urls[link] += f", {site_name}"

            site_stats[site_num] = {
                "name": site_name,
                "found": len(links),
                "expected": expected,
                "match": expected is None or expected == len(links),
            }

            time.sleep(0.5)
        except Exception as e:
            print(f"  Error fetching site {site_num}: {e}")
            site_stats[site_num] = {"name": get_site_name(site_num), "error": str(e)}

    print("\n" + "=" * 60)
    print("SITE STATISTICS")
    print("=" * 60)

    total_found = 0
    for site_num, stats in site_stats.items():
        name = stats.get("name", f"Site {site_num}")
        if "error" in stats:
            print(f"Site {site_num} ({name}): ERROR - {stats['error']}")
        else:
            match_str = "✓" if stats["match"] else "✗"
            print(
                f"Site {site_num} ({name}): {stats['found']} stories {match_str} (expected: {stats.get('expected', 'N/A')})"
            )
            total_found += stats["found"]

    print("=" * 60)
    print(f"Total unique stories found: {len(all_story_urls)}")

    urls_list = list(all_story_urls.keys())

    with open("story_urls.json", "w") as f:
        json.dump(urls_list, f, indent=2)
    print("Saved story URLs to story_urls.json")

    site_mapping = {url: site for url, site in all_story_urls.items()}
    with open("story_site_mapping.json", "w") as f:
        json.dump(site_mapping, f, indent=2)
    print("Saved site mapping to story_site_mapping.json")


if __name__ == "__main__":
    main()
