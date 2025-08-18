#!/usr/bin/env python3
"""Check for duplicate media records and recent media activity."""

import asyncio
import aiohttp
import os

async def check_media_issues():
    supabase_url = os.getenv('SUPABASE_URL', 'https://suzxmthipriaglududga.supabase.co')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1enhtdGhpcHJpYWdsdWR1ZGdhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQ2ODUxMiwiZXhwIjoyMDcxMDQ0NTEyfQ.uAF5QDhBXDmI9LdAmeMcJfcc5VTtRT063zmXQShES-A')
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # Check all media records
        print("=== CHECKING FOR DUPLICATES ===")
        async with session.get(
            f"{supabase_url}/rest/v1/archived_media?order=archived_at.desc",
            headers=headers
        ) as resp:
            if resp.status == 200:
                media_records = await resp.json()
                print(f"Total media records: {len(media_records)}")
                
                # Group by event_id to find duplicates
                event_groups = {}
                for record in media_records:
                    event_id = record['event_id']
                    if event_id not in event_groups:
                        event_groups[event_id] = []
                    event_groups[event_id].append(record)
                
                duplicates = {k: v for k, v in event_groups.items() if len(v) > 1}
                
                if duplicates:
                    print(f"\n🚨 Found {len(duplicates)} events with duplicate media records:")
                    for event_id, records in duplicates.items():
                        print(f"\nEvent {event_id}: {len(records)} duplicates")
                        for i, record in enumerate(records):
                            print(f"  #{i+1}: ID {record['id']}, archived at {record['archived_at']}")
                else:
                    print("✅ No duplicates found")
                
                # Show recent media (last 10)
                print(f"\n=== RECENT MEDIA RECORDS ===")
                for i, record in enumerate(media_records[:10]):
                    print(f"\n{i+1}. Event: {record['event_id']}")
                    print(f"   Type: {record['media_type']}")
                    print(f"   Filename: {record['original_filename']}")
                    print(f"   Matrix URL: {record['matrix_url']}")
                    print(f"   Storage Path: {record['storage_path'] or 'EMPTY'}")
                    print(f"   Public URL: {record['public_url'] or 'EMPTY'}")
                    print(f"   Archived: {record['archived_at']}")
                    
            else:
                error = await resp.text()
                print(f"❌ Failed to get media records: {resp.status} - {error}")
        
        # Check recent messages for new media
        print(f"\n=== RECENT MESSAGES (Last 5) ===")
        async with session.get(
            f"{supabase_url}/rest/v1/archived_messages?order=archived_at.desc&limit=5",
            headers=headers
        ) as resp:
            if resp.status == 200:
                messages = await resp.json()
                for msg in messages:
                    content = msg['content']
                    has_media = content.get('url', '').startswith('mxc://')
                    print(f"\nMessage: {msg['event_id']}")
                    print(f"  Room: {msg['room_id']}")
                    print(f"  Type: {content.get('msgtype', 'unknown')}")
                    print(f"  Has MXC URL: {'✓' if has_media else '✗'}")
                    if has_media:
                        print(f"  MXC URL: {content.get('url')}")
                    print(f"  Archived: {msg['archived_at']}")

if __name__ == "__main__":
    asyncio.run(check_media_issues())