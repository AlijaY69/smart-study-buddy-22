#!/usr/bin/env python3
"""
Fix existing assignments that have split topics.
Merges split topics like ["Natural", "Language", "Processing"] into ["Natural Language Processing"]
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

def get_supabase_client():
    """Get Supabase connection details."""
    url = os.getenv('VITE_SUPABASE_URL') or os.getenv('SUPABASE_URL')
    key = os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')

    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

    return {
        'url': url,
        'headers': {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
    }

def fix_split_topics():
    """Fix all assignments with split topics."""
    client = get_supabase_client()

    # Get all assignments
    url = f"{client['url']}/rest/v1/assignments?select=*"
    response = requests.get(url, headers=client['headers'])

    if response.status_code != 200:
        print(f"Error fetching assignments: {response.status_code} {response.text}")
        return

    assignments = response.json()
    print(f"Found {len(assignments)} assignments")

    fixed_count = 0

    for assignment in assignments:
        topics = assignment.get('topics', [])

        # Skip if empty or already a single topic
        if not topics or len(topics) <= 1:
            continue

        # Check if topics look like they were split (all short words)
        # If most topics are short (< 15 chars), likely they were split
        avg_length = sum(len(t) for t in topics) / len(topics)

        if avg_length < 15 and len(topics) > 1:
            # Merge topics back together
            merged_topic = ' '.join(topics)
            new_topics = [merged_topic]

            print(f"\nFixing assignment: {assignment['title']}")
            print(f"  Old topics: {topics}")
            print(f"  New topics: {new_topics}")

            # Update the assignment
            update_url = f"{client['url']}/rest/v1/assignments?id=eq.{assignment['id']}"
            update_data = {'topics': new_topics}

            update_response = requests.patch(
                update_url,
                headers=client['headers'],
                json=update_data
            )

            if update_response.status_code in [200, 204]:
                print(f"  ✓ Updated successfully")
                fixed_count += 1
            else:
                print(f"  ✗ Error updating: {update_response.status_code} {update_response.text}")

    print(f"\n{'='*60}")
    print(f"Fixed {fixed_count} assignments")
    print(f"{'='*60}")

if __name__ == '__main__':
    try:
        fix_split_topics()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
