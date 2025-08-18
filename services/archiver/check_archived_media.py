#!/usr/bin/env python3
"""Check archived media records in Supabase."""

import asyncio
import aiohttp
import os
import json

async def check_archived_media():
    supabase_url = os.getenv('SUPABASE_URL', 'https://suzxmthipriaglududga.supabase.co')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1enhtdGhpcHJpYWdsdWR1ZGdhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQ2ODUxMiwiZXhwIjoyMDcxMDQ0NTEyfQ.uAF5QDhBXDmI9LdAmeMcJfcc5VTtRT063zmXQShES-A')
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # Get archived media records
        async with session.get(
            f"{supabase_url}/rest/v1/archived_media?order=archived_at.desc",
            headers=headers
        ) as resp:
            if resp.status == 200:
                media_records = await resp.json()
                print(f"📎 Found {len(media_records)} media records:")
                
                for record in media_records:
                    print(f"\n🔹 Event ID: {record['event_id']}")
                    print(f"   Media Type: {record['media_type']}")
                    print(f"   Filename: {record['original_filename']}")
                    print(f"   MIME Type: {record['mime_type']}")
                    print(f"   File Size: {record['file_size']} bytes")
                    print(f"   Matrix URL: {record['matrix_url']}")
                    print(f"   Storage Path: {record['storage_path']}")
                    print(f"   Public URL: {record['public_url']}")
                    print(f"   Archived: {record['archived_at']}")
                    
            else:
                error = await resp.text()
                print(f"❌ Failed to get media records: {resp.status} - {error}")

if __name__ == "__main__":
    asyncio.run(check_archived_media())