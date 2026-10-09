"""Create a Medium *draft* from a blog Markdown file. Never publishes.

The integration token is read from MEDIUM_TOKEN only (never a CLI argument, so it
cannot land in shell history or process listings). Medium has restricted new
integration tokens, so this may be unusable for your account.

    MEDIUM_TOKEN=... python scripts/publish_medium_draft.py \
        docs/blogs/2026-10-09-soc-incident-response-pipeline.md --tags cybersecurity soc automation
    python scripts/publish_medium_draft.py <file> --dry-run     # no token, no network
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import requests

API = "https://api.medium.com/v1"
TIMEOUT = 20
MAX_TAGS = 5  # Medium ignores any beyond five
REPO_BLOB = "https://github.com/Mangesh-Bhattacharya/soc-incident-response-pipeline/blob/main"


def prepare(markdown: str, source: Path, repo_root: Path) -> tuple[str, str]:
    """Return (title, body): H1 lifted out as the title, HTML comments and the
    leading companion-file note dropped, relative links rewritten to GitHub URLs."""
    text = re.sub(r"<!--.*?-->\n?", "", markdown, flags=re.DOTALL)
    match = re.match(r"\s*#\s+(?P<title>.+?)\s*\n", text)
    if not match:
        raise ValueError("first line must be an H1 title")
    title = match["title"]
    body = text[match.end():].lstrip("\n")
    body = re.sub(r"^\*Draft for Medium\..*\*\n+", "", body)

    def _absolute(m: re.Match[str]) -> str:
        target = m["target"]
        if re.match(r"^(https?:|#|mailto:)", target):
            return m[0]
        resolved = (source.parent / target).resolve()
        try:
            rel = resolved.relative_to(repo_root.resolve())
        except ValueError:
            return m["text"]  # link escapes the repo: keep the text, drop the link
        return f"[{m['text']}]({REPO_BLOB}/{rel.as_posix()})"

    body = re.sub(r"(?P<label>\[(?P<text>[^\]]*)\]\((?P<target>[^)\s]+)\))", _absolute, body)
    return title, body


def create_draft(token: str, title: str, body: str, tags: list[str]) -> str:
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    me = requests.get(f"{API}/me", headers=headers, timeout=TIMEOUT)
    me.raise_for_status()
    user_id = me.json()["data"]["id"]
    post = requests.post(
        f"{API}/users/{user_id}/posts",
        headers=headers,
        json={
            "title": title,
            "contentFormat": "markdown",
            "content": f"# {title}\n\n{body}",
            "tags": tags[:MAX_TAGS],
            "publishStatus": "draft",
        },
        timeout=TIMEOUT,
    )
    post.raise_for_status()
    return post.json()["data"]["url"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", type=Path)
    parser.add_argument("--tags", nargs="*", default=["cybersecurity", "soc", "automation"])
    parser.add_argument("--dry-run", action="store_true", help="Print the prepared post; no token or network needed")
    args = parser.parse_args()

    try:
        title, body = prepare(args.file.read_text(encoding="utf-8"), args.file, Path(__file__).resolve().parent.parent)
    except (OSError, ValueError) as exc:
        print(f"Cannot prepare {args.file}: {exc}", file=sys.stderr)
        return 2

    if args.dry_run:
        print(f"TITLE: {title}\nTAGS: {args.tags[:MAX_TAGS]}\n\n{body}")
        return 0

    token = os.environ.get("MEDIUM_TOKEN", "")
    if not token:
        print("MEDIUM_TOKEN is not set", file=sys.stderr)
        return 2
    try:
        print(f"Draft created (not published): {create_draft(token, title, body, args.tags)}")
    except requests.RequestException as exc:
        status = getattr(getattr(exc, "response", None), "status_code", "n/a")
        print(f"Medium API call failed (HTTP {status}); check the token and that Medium still accepts it", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
