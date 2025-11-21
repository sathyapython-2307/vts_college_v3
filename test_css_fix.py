#!/usr/bin/env python
import urllib.request
import re

url = "http://127.0.0.1:8000/course/ui-ux-designing/"

with urllib.request.urlopen(url) as response:
    content = response.read().decode('utf-8')

# Extract inline styles and CSS for play-overlay
print("Checking for .play-overlay CSS rules:")
print("="*60)

# Look for CSS rules
plays = re.findall(r'\.play-overlay\s*\{[^}]*\}', content, re.DOTALL)
print(f"Found {len(plays)} .play-overlay CSS rule(s):\n")

for i, rule in enumerate(plays):
    print(f"Rule {i+1}:")
    print(rule[:200])
    print()

# Extract first play button
pattern = r'<a[^>]*class="[^"]*play-overlay[^"]*"[^>]*>.*?<\/a>'
match = re.search(pattern, content, re.DOTALL)

if match:
    print("="*60)
    print("First Play button HTML:")
    print("="*60)
    print(match.group(0)[:300])
else:
    print("✗ Play button not found")
