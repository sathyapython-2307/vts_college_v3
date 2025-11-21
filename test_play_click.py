#!/usr/bin/env python
"""
Test script to fetch the page and simulate Play button interaction.
Extracts the first video item's attributes and logs what the JS would do.
"""
import urllib.request
import re
import json

url = "http://127.0.0.1:8000/course/ui-ux-designing/"

try:
    with urllib.request.urlopen(url) as response:
        content = response.read().decode('utf-8')
    
    # Extract first video item's data attributes
    pattern = r'<li[^>]*class="[^"]*video-item[^"]*"[^>]*data-video-url="([^"]*)"[^>]*data-video-type="([^"]*)"[^>]*data-allowed="([^"]*)"[^>]*data-item-id="([^"]*)"[^>]*data-course-id="([^"]*)"'
    match = re.search(pattern, content)
    
    if match:
        video_url = match.group(1)
        video_type = match.group(2)
        allowed = match.group(3)
        item_id = match.group(4)
        course_id = match.group(5)
        
        print("=" * 60)
        print("FIRST VIDEO ITEM ATTRIBUTES")
        print("=" * 60)
        print(f"Video URL: {video_url}")
        print(f"Video Type: {video_type}")
        print(f"Allowed: {allowed}")
        print(f"Item ID: {item_id}")
        print(f"Course ID: {course_id}")
        print()
        
        # Simulate Play click logic
        print("=" * 60)
        print("WHEN USER CLICKS PLAY (Simulated JS Logic)")
        print("=" * 60)
        
        if not allowed.lower() == 'true':
            print("❌ BLOCKED: User not allowed to play (not paid)")
        elif not video_url:
            print("❌ ERROR: No video URL available")
        else:
            print(f"✓ Would call: openVideo('{video_url[:50]}...', '{video_type}', {item_id}, {course_id})")
            print()
            print("  → Modal would open")
            print(f"  → Video element created with type='{video_type}'")
            if video_type == 'file':
                print(f"  → Source tag src='{video_url}'")
                print("  → Video.load() called")
                print("  → Waiting for video to play...")
                print("  → On ended or 80% watched: markVideoWatched() POST to API")
            elif video_type == 'external':
                print("  → YouTube embed would open (autoplay after 3s)")
            
    else:
        print("❌ ERROR: Could not find any video items in rendered HTML")
        
        # Debug: check if there's any mention of video-item
        if 'video-item' in content:
            print("But 'video-item' class WAS found in HTML")
            print("Checking for any <li> with video-item class...")
            lis = re.findall(r'<li[^>]*class="[^"]*video-item[^"]*"', content)
            print(f"Found {len(lis)} <li> elements with video-item class")
            if lis:
                print("First one:", lis[0][:100])
        else:
            print("'video-item' class NOT found anywhere in HTML")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
