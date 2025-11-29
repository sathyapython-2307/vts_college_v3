#!/usr/bin/env python3
"""
Simple post-deploy verification script.

Usage:
  TARGET_URL=https://example.com python scripts/post_deploy_check.py

Checks:
  - GET / returns 200
  - GET /static/css/style.css (if present) returns 200
  - GET /static/js/main.js (if present) returns 200
  - GET /static/images/logo.png (if present) returns 200

Exits 0 on success, non-zero on failure.
"""
import os
import sys
import requests

def check_url(url, session):
    try:
        r = session.get(url, timeout=10)
        print(f"{url} -> {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"{url} -> ERROR: {e}")
        return False

def main():
    base = os.environ.get('TARGET_URL') or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not base:
        print('Usage: TARGET_URL=https://example.com python scripts/post_deploy_check.py')
        sys.exit(2)

    if base.endswith('/'):
        base = base[:-1]

    session = requests.Session()
    checks = [
        base + '/',
        base + '/static/css/style.css',
        base + '/static/js/main.js',
        base + '/static/images/logo.png',
    ]

    all_ok = True
    for url in checks:
        ok = check_url(url, session)
        # If a static asset returns 404 it's possible it's not present; treat
        # homepage 200 as required, but treat missing static assets as warnings.
        if url.endswith('/') and not ok:
            all_ok = False
            break
        elif url.endswith(('.css', '.js', '.png')) and not ok:
            print(f"WARNING: static asset missing or not served: {url}")

    if not all_ok:
        print('Post-deploy verification failed.')
        sys.exit(1)

    print('Post-deploy verification succeeded.')
    sys.exit(0)

if __name__ == '__main__':
    main()
