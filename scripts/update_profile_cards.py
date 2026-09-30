"""Refresh profile images without depending on live README image services."""

from __future__ import annotations

import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CONTRIBUTIONS_URL = "https://github.com/users/zklou/contributions"
TROPHY_URL = (
    "https://trophygithubreadmelang.cybee.dpdns.org/"
    "?username=zklou&row=2&column=3&margin-w=10&margin-h=15"
)


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "zklou-profile-cards/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def update_contributions() -> None:
    html = fetch(CONTRIBUTIONS_URL).decode("utf-8")
    match = re.search(r'id="js-contribution-activity-description"[^>]*>\s*([\d,]+)\s+contributions\s+in the last year', html)
    if not match:
        raise RuntimeError("GitHub contribution total was not found")
    count = match.group(1)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="680" height="142" viewBox="0 0 680 142" role="img" aria-label="{count} GitHub contributions in the last year">
  <rect x="1" y="1" width="678" height="140" rx="16" fill="#0d1117" stroke="#30363d" stroke-width="2"/>
  <circle cx="48" cy="49" r="11" fill="#39d353"/>
  <text x="73" y="56" fill="#c9d1d9" font-family="Arial, sans-serif" font-size="19" font-weight="600">GitHub contributions</text>
  <text x="39" y="113" fill="#ffffff" font-family="Arial, sans-serif" font-size="48" font-weight="700">{count}</text>
  <text x="216" y="108" fill="#8b949e" font-family="Arial, sans-serif" font-size="17">in the last year · updated {date} UTC</text>
</svg>
'''
    (ASSETS / "contributions.svg").write_text(svg, encoding="utf-8")
    print(f"GitHub contributions: {count}")


def update_trophies() -> None:
    try:
        svg = fetch(TROPHY_URL)
        root = ET.fromstring(svg)
        if not root.tag.endswith("svg") or len(svg) < 1000:
            raise ValueError("trophy response was not a usable SVG")
        (ASSETS / "trophies.svg").write_bytes(svg)
        print("Trophies refreshed")
    except (OSError, ValueError, ET.ParseError) as exc:
        if not (ASSETS / "trophies.svg").exists():
            raise
        print(f"Trophy service unavailable; keeping the last good image: {exc}")


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    update_contributions()
    update_trophies()
