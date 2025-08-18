#!/usr/bin/env python3
"""Clean up duplicate media records."""

import asyncio
import aiohttp
import os

async def cleanup_duplicates():
    supabase_url = os.getenv('SUPABASE_URL', 'https://suzxmthipriaglududga.supabase.co')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1enhtdGhpcHJpYWdsdWR1ZGdhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQ2ODUxMiwiZXhwIjoyMDcxMDQ0NTEyfQ.uAF5QDhBXDmI9LdAmeMcJfcc5VTtRT063zmXQShES-A')
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # Get all media records
        async with session.get(
            f"{supabase_url}/rest/v1/archived_media?order=archived_at.asc",
            headers=headers
        ) as resp:
            if resp.status == 200:
                media_records = await resp.json()
                print(f"Found {len(media_records)} media records")
                
                # Group by event_id
                event_groups = {}
                for record in media_records:
                    event_id = record['event_id']
                    if event_id not in event_groups:
                        event_groups[event_id] = []
                    event_groups[event_id].append(record)
                
                # Find and remove duplicates (keep oldest)
                deleted_count = 0
                for event_id, records in event_groups.items():
                    if len(records) > 1:
                        print(f"\nEvent {event_id}: {len(records)} records")
                        # Keep the first (oldest) record, delete the rest
                        to_delete = records[1:]  # Skip first record
                        for record in to_delete:
                            print(f"  Deleting duplicate ID {record['id']}")
                            
                            async with session.delete(
                                f"{supabase_url}/rest/v1/archived_media?id=eq.{record['id']}",
                                headers=headers
                            ) as del_resp:
                                if del_resp.status in [200, 204]:
                                    deleted_count += 1
                                    print(f"    ✓ Deleted")
                                else:
                                    error = await del_resp.text()
                                    print(f"    ✗ Failed: {del_resp.status} - {error}")
                
                print(f"\n✓ Cleanup complete: {deleted_count} duplicates removed")
                
            else:
                error = await resp.text()
                print(f"❌ Failed to get media records: {resp.status} - {error}")

if __name__ == "__main__":
    asyncio.run(cleanup_duplicates())