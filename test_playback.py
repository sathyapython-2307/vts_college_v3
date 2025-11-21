#!/usr/bin/env python
import urllib.request
import urllib.error
import re

url = "http://127.0.0.1:8000/course/ui-ux-designing/"

try:
    with urllib.request.urlopen(url) as response:
        content = response.read().decode('utf-8')
        
    # Find video items
    pattern = r'<li[^>]*class="[^"]*video-item[^"]*"[^>]*data-video-url="([^"]*)"[^>]*data-video-type="([^"]*)"[^>]*data-item-id="([^"]*)"[^>]*data-course-id="([^"]*)"'
    matches = list(re.finditer(pattern, content))
    
    print(f"✓ Page fetched successfully")
    print(f"Found {len(matches)} video items\n")
    
    for i, m in enumerate(matches):
        url_val = m.group(1)
        type_val = m.group(2)
        item_id = m.group(3)
        course_id = m.group(4)
        print(f"Item {i+1}:")
        print(f"  video-url: {url_val[:80]}")
        print(f"  video-type: {type_val}")
        print(f"  item-id: {item_id}")
        print(f"  course-id: {course_id}\n")
    
    # Check for key elements
    print("Key elements:")
    print(f"  show_congratulations: {'✓' if 'show_congratulations' in content else '✗'}")
    print(f"  video-modal: {'✓' if 'video-modal' in content else '✗'}")
    print(f"  openVideo function: {'✓' if 'function openVideo' in content else '✗'}")
    print(f"  play-overlay: {'✓' if 'play-overlay' in content else '✗'}")
    
except urllib.error.URLError as e:
    print(f"✗ Error: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")
