#!/usr/bin/env python
import urllib.request
import re

url = "http://127.0.0.1:8000/course/ui-ux-designing/"

with urllib.request.urlopen(url) as response:
    content = response.read().decode('utf-8')

# Find the first video item and extract full HTML
pattern = r'<li class="schedule-item video-item".*?<\/li>'
match = re.search(pattern, content, re.DOTALL)

if match:
    item_html = match.group(0)
    
    # Check for play-overlay
    if 'play-overlay' in item_html:
        print("✓ Play button found in HTML")
        
        # Extract play button
        play_match = re.search(r'<a[^>]*class="[^"]*play-overlay[^"]*"[^>]*>.*?<\/a>', item_html, re.DOTALL)
        if play_match:
            print("\nPlay button HTML:")
            print(play_match.group(0)[:200])
    else:
        print("✗ Play button NOT in first video item!")
        
    # Check item content div
    if 'item-content' in item_html:
        print("\n✓ item-content div found")
    
    # Check if it's a paid user or first day
    if 'data-allowed="true"' in item_html:
        print("✓ User has allowed access (data-allowed=true)")
    else:
        print("✗ User access denied (data-allowed!=true)")
        
    print("\n" + "="*60)
    print("FULL ITEM HTML (first 500 chars):")
    print("="*60)
    print(item_html[:500])
    
else:
    print("✗ Could not find video item")
