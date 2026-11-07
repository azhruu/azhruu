#!/usr/bin/env python3
"""Regenerate contribution-streak.svg from GitHub's public contribution data.
Runs daily via .github/workflows/update-streak.yml (stdlib only)."""
import re
import sys
import urllib.request
from datetime import date, timedelta

USER = "azhruu"
OUT = sys.argv[1] if len(sys.argv) > 1 else "contribution-streak.svg"

req = urllib.request.Request(
    f"https://github.com/users/{USER}/contributions",
    headers={"User-Agent": "Mozilla/5.0"},
)
html = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")

tds = dict(re.findall(r'data-date="(\d{4}-\d{2}-\d{2})" id="(contribution-day-component-[\d-]+)"', html))
tips = dict(re.findall(r'for="(contribution-day-component-[\d-]+)"[^>]*>([^<]+)</tool-tip>', html))

days = {}
for dstr, cid in tds.items():
    m = re.match(r"(\d+) contribution", tips.get(cid, ""))
    days[date.fromisoformat(dstr)] = int(m.group(1)) if m else 0
if not days:
    sys.exit("no contribution days parsed")

total = sum(days.values())
start, end = min(days), max(days)

longest = run = 0
d = start
while d <= end:
    run = run + 1 if days.get(d, 0) > 0 else 0
    longest = max(longest, run)
    d += timedelta(days=1)

cur = 0
d = end
if days.get(d, 0) == 0:
    d -= timedelta(days=1)
streak_end = d
while d >= start and days.get(d, 0) > 0:
    cur += 1
    d -= timedelta(days=1)
streak_start = streak_end - timedelta(days=cur - 1) if cur else streak_end

fmt = lambda dt: dt.strftime("%b %d, %Y").replace(" 0", " ")
fmt_short = lambda dt: dt.strftime("%b %d").replace(" 0", " ")
streak_range = f"{fmt_short(streak_start)} - {fmt_short(streak_end)}" if cur else "-"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="495" height="195" viewBox="0 0 495 195">
  <rect x="0.5" y="0.5" width="494" height="194" rx="6" fill="#1a1b27" stroke="#414868"/>
  <line x1="165" y1="40" x2="165" y2="155" stroke="#414868" stroke-width="1"/>
  <line x1="330" y1="40" x2="330" y2="155" stroke="#414868" stroke-width="1"/>
  <text x="82" y="80" text-anchor="middle" font-family="Segoe UI, Ubuntu, sans-serif" font-size="28" font-weight="700" fill="#7aa2f7">{total}</text>
  <text x="82" y="112" text-anchor="middle" font-family="Segoe UI, Ubuntu, sans-serif" font-size="13" fill="#c0caf5">Total Contributions</text>
  <text x="82" y="134" text-anchor="middle" font-family="Segoe UI, Ubuntu, sans-serif" font-size="11" fill="#565f89">{fmt(start)} - Present</text>
  <text x="247" y="80" text-anchor="middle" font-family="Segoe UI, Ubuntu, sans-serif" font-size="28" font-weight="700" fill="#ff9e64">{cur}</text>
  <text x="247" y="112" text-anchor="middle" font-family="Segoe UI, Ubuntu, sans-serif" font-size="13" fill="#c0caf5">Current Streak</text>
  <text x="247" y="134" text-anchor="middle" font-family="Segoe UI, Ubuntu, sans-serif" font-size="11" fill="#565f89">{streak_range}</text>
  <text x="412" y="80" text-anchor="middle" font-family="Segoe UI, Ubuntu, sans-serif" font-size="28" font-weight="700" fill="#7aa2f7">{longest}</text>
  <text x="412" y="112" text-anchor="middle" font-family="Segoe UI, Ubuntu, sans-serif" font-size="13" fill="#c0caf5">Longest Streak</text>
  <text x="412" y="134" text-anchor="middle" font-family="Segoe UI, Ubuntu, sans-serif" font-size="11" fill="#565f89">days</text>
</svg>
'''
with open(OUT, "w") as f:
    f.write(svg)
print(f"total={total} current_streak={cur} longest={longest} -> {OUT}")
