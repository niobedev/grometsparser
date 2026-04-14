import os
import re
import argparse


def is_broken(content):
    if re.search(r"_[^_\n]+?\n\n[^_]+?_", content):
        return True, "Multiline italics with blank lines"

    if re.search(r"_[^_\n]+? \s*_", content):
        return True, "Italics with trailing spaces before closing underscore"

    if re.search(r"_\s+[^_\n]+?_", content) or re.search(r"_[^_\n]+?\s+_", content):
        return True, "Italics with leading or trailing spaces"

    if "___" in content:
        return True, "Triple underscores detected"

    if re.search(r"_\s+\*\*Author\'s Note:\*\*", content) or re.search(
        r"\*\*Author\'s Note:\*\*\s+_", content
    ):
        return True, "Broken Author's Note formatting"

    if content and not content.endswith("\n"):
        return True, "Missing trailing newline"

    return False, ""


def main():
    parser = argparse.ArgumentParser(
        description="Detect and delete stories with broken markdown."
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete the broken stories after detection.",
    )
    parser.add_argument(
        "--force", action="store_true", help="Force deletion without confirmation."
    )
    args = parser.parse_args()

    stories_dir = "website/content/stories"

    if not os.path.exists(stories_dir):
        print(f"Directory {stories_dir} not found. Run 'make convert' first.")
        return

    broken_files = []

    files = [f for f in os.listdir(stories_dir) if f.endswith(".md")]
    print(f"Scanning {len(files)} files in {stories_dir}...")

    for filename in files:
        filepath = os.path.join(stories_dir, filename)
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        broken, reason = is_broken(content)
        if broken:
            broken_files.append((filename, reason))

    if not broken_files:
        print("No broken stories detected.")
        return

    print(f"\nDetected {len(broken_files)} broken stories:")
    for filename, reason in broken_files:
        print(f" - {filename}: {reason}")

    if args.delete:
        if args.force:
            confirm = "y"
        else:
            confirm = input(
                f"\nAre you sure you want to delete these {len(broken_files)} files? (y/N): "
            )

        if confirm.lower() == "y":
            for filename, _ in broken_files:
                p = os.path.join(stories_dir, filename)
                if os.path.exists(p):
                    os.remove(p)

            print(
                f"\nDeleted {len(broken_files)} files. Now you can run 'make convert' to re-convert them."
            )
        else:
            print("\nDeletion cancelled.")
    else:
        print(f"\nRun with --delete to delete these {len(broken_files)} files.")


if __name__ == "__main__":
    main()
