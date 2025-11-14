#!/usr/bin/env python3
"""
Test all RSS feeds in config/rss-sources.yaml
Identify working and broken feeds
"""

import yaml
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import time
from collections import defaultdict

# Headers to bypass basic bot detection
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/rss+xml, application/xml, text/xml, */*',
    'Accept-Language': 'en-US,en;q=0.9',
}

TIMEOUT = 10

def test_feed(url, name):
    """Test if an RSS feed is accessible and valid"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)

        if response.status_code == 200:
            # Try to parse as XML
            try:
                root = ET.fromstring(response.content)
                # Check if it's a valid RSS/Atom feed
                if root.tag in ['{http://www.w3.org/2005/Atom}feed', 'rss', 'feed']:
                    # Count items
                    items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
                    return {
                        'status': 'OK',
                        'code': 200,
                        'items': len(items),
                        'type': root.tag,
                        'error': None
                    }
                else:
                    return {
                        'status': 'INVALID',
                        'code': 200,
                        'items': 0,
                        'type': root.tag,
                        'error': f'Not a valid RSS/Atom feed (root tag: {root.tag})'
                    }
            except ET.ParseError as e:
                return {
                    'status': 'PARSE_ERROR',
                    'code': 200,
                    'items': 0,
                    'type': None,
                    'error': f'XML parse error: {str(e)[:100]}'
                }
        else:
            return {
                'status': 'HTTP_ERROR',
                'code': response.status_code,
                'items': 0,
                'type': None,
                'error': f'HTTP {response.status_code}'
            }
    except requests.exceptions.Timeout:
        return {
            'status': 'TIMEOUT',
            'code': None,
            'items': 0,
            'type': None,
            'error': f'Timeout after {TIMEOUT}s'
        }
    except requests.exceptions.SSLError as e:
        return {
            'status': 'SSL_ERROR',
            'code': None,
            'items': 0,
            'type': None,
            'error': 'SSL certificate error'
        }
    except requests.exceptions.ConnectionError as e:
        return {
            'status': 'CONNECTION_ERROR',
            'code': None,
            'items': 0,
            'type': None,
            'error': 'Connection failed'
        }
    except Exception as e:
        return {
            'status': 'ERROR',
            'code': None,
            'items': 0,
            'type': None,
            'error': str(e)[:100]
        }

def main():
    print("=" * 80)
    print("RSS FEED VALIDATOR")
    print("=" * 80)
    print()

    # Load config
    with open('config/rss-sources.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Flatten all feeds
    all_feeds = []
    for category, feeds in config.items():
        if isinstance(feeds, list):
            for feed in feeds:
                feed['config_category'] = category
                all_feeds.append(feed)

    print(f"Total feeds to test: {len(all_feeds)}\n")

    # Test results
    results = {
        'working': [],
        'broken': [],
        'total': len(all_feeds)
    }

    status_counts = defaultdict(int)

    # Test each feed
    for i, feed in enumerate(all_feeds, 1):
        name = feed['name']
        url = feed['url']
        category = feed['config_category']

        print(f"[{i:3d}/{len(all_feeds)}] Testing: {name[:50]:<50} ", end='', flush=True)

        result = test_feed(url, name)
        status_counts[result['status']] += 1

        if result['status'] == 'OK':
            print(f"✓ OK ({result['items']} items)")
            results['working'].append({
                'name': name,
                'url': url,
                'category': category,
                'items': result['items']
            })
        else:
            print(f"✗ {result['status']}")
            if result['error']:
                print(f"      Error: {result['error']}")
            results['broken'].append({
                'name': name,
                'url': url,
                'category': category,
                'status': result['status'],
                'code': result['code'],
                'error': result['error']
            })

        # Small delay to avoid rate limiting
        time.sleep(0.5)

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total feeds tested: {results['total']}")
    print(f"Working feeds: {len(results['working'])} ({len(results['working'])/results['total']*100:.1f}%)")
    print(f"Broken feeds: {len(results['broken'])} ({len(results['broken'])/results['total']*100:.1f}%)")
    print()
    print("Status breakdown:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")

    # Save results
    print("\n" + "=" * 80)
    print("BROKEN FEEDS DETAILS")
    print("=" * 80)

    if results['broken']:
        for feed in results['broken']:
            print(f"\n✗ {feed['name']}")
            print(f"  URL: {feed['url']}")
            print(f"  Category: {feed['category']}")
            print(f"  Status: {feed['status']}")
            if feed['error']:
                print(f"  Error: {feed['error']}")
    else:
        print("All feeds are working! 🎉")

    # Save to files
    with open('/tmp/working_feeds.txt', 'w') as f:
        for feed in results['working']:
            f.write(f"{feed['name']}\t{feed['url']}\n")

    with open('/tmp/broken_feeds.txt', 'w') as f:
        for feed in results['broken']:
            f.write(f"{feed['name']}\t{feed['url']}\t{feed['status']}\n")

    print("\n" + "=" * 80)
    print(f"✓ Results saved to /tmp/working_feeds.txt and /tmp/broken_feeds.txt")
    print("=" * 80)

if __name__ == '__main__':
    main()
