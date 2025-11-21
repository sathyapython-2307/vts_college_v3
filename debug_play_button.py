#!/usr/bin/env python
import urllib.request
import re

url = "http://127.0.0.1:8000/course/ui-ux-designing/"

with urllib.request.urlopen(url) as response:
    content = response.read().decode('utf-8')

# Find first video item and extract FULL HTML including all styling
pattern = r'<li class="schedule-item video-item".*?<\/li>'
match = re.search(pattern, content, re.DOTALL)

if match:
    item_html = match.group(0)
    
    # Extract the play button element
    play_pattern = r'<a[^>]*class="[^"]*play-overlay[^"]*"[^>]*>.*?<\/a>'
    play_match = re.search(play_pattern, item_html, re.DOTALL)
    
    if play_match:
        play_btn = play_match.group(0)
        print("PLAY BUTTON HTML:")
        print("="*70)
        print(play_btn)
        print()
        
        # Check styling
        print("ANALYSIS:")
        print("="*70)
        
        # Check if button has inline styles that hide it
        if 'style="' in play_btn:
            style_match = re.search(r'style="([^"]*)"', play_btn)
            if style_match:
                style = style_match.group(1)
                print(f"Inline style: {style}")
                if 'display:none' in style.lower():
                    print("❌ PROBLEM: Button is hidden (display:none)")
        else:
            print("No inline styles on button")
        
        # Check the parent structure
        print("\nPARENT STRUCTURE:")
        print("="*70)
        # Extract the item-content div
        content_match = re.search(r'<div class="item-content">(.*?)<\/div>', item_html, re.DOTALL)
        if content_match:
            content_div = content_match.group(1)
            print("Content div (first 400 chars):")
            print(content_div[:400])
            
            # Count how many nested divs
            open_divs = content_div.count('<div')
            close_divs = content_div.count('</div>')
            print(f"\nDiv nesting: {open_divs} opens, {close_divs} closes")
    else:
        print("✗ Play button not found in item HTML")
else:
    print("✗ Video item not found")
