#!/usr/bin/env python3
"""
Checks a webpage for changes and sends a phone push notification via ntfy.sh
when the content changes.

Designed to run on a schedule (e.g. via GitHub Actions, cron, or Task Scheduler).
State (the last-seen hash) is persisted to a small JSON file so it survives
between runs.
"""

import hashlib
import json
import os
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---- Configuration (edit this list to add/remove pages to watch) ---------
URLS = [
    "https://transit.yahoo.co.jp/diainfo/pref/13",
    "https://amaterasu-yokohama.com/schedule?day=2026-09-07&from=2026-09-01",
]
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")  # set this to your unique topic name
STATE_FILE = Path(os.environ.get("STATE_FILE", "state.json"))
# ----------------------------------------------------------------------------


def fetch_content(url: str) -> str:
    """Fetch the page and return the meaningful text content (ignoring noise)."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Narrow to the main schedule section if we can find it, so unrelated
    # page chrome (ads, banners, nav) doesn't cause false-positive alerts.
    main = soup.select_one("main") or soup.body or soup

    # Strip obviously noisy/irrelevant elements (scripts, styles, ad banners).
    for tag in main.select("script, style, noscript"):
        tag.decompose()

    text = main.get_text(separator="\n", strip=True)
    return text


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


def send_notification(title: str, message: str) -> None:
    if not NTFY_TOPIC:
        print("NTFY_TOPIC not set — skipping push notification.")
        return
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            headers={
                "Title": title.encode("utf-8"),
                "Priority": "default",
                "Tags": "bell",
            },
            timeout=15,
        )
    except requests.RequestException as e:
        print(f"Failed to send notification: {e}", file=sys.stderr)


def main() -> None:
    state = load_state()

    for url in URLS:
        print(f"Checking: {url}")
        try:
            text = fetch_content(url)
        except requests.RequestException as e:
            print(f"  Failed to fetch — skipping this run: {e}", file=sys.stderr)
            continue

        new_hash = content_hash(text)
        old_hash = state.get(url, {}).get("hash")

        if old_hash is None:
            print("  First run for this URL — saving baseline, no notification sent.")
        elif old_hash != new_hash:
            print("  Change detected — sending notification.")
            send_notification(
                title="Page updated",
                message=f"This page changed:\n{url}",
            )
        else:
            print("  No change.")

        state[url] = {"hash": new_hash}

    save_state(state)


if __name__ == "__main__":
    main()
