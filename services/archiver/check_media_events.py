#!/usr/bin/env python3
"""Check for media events in recent messages."""

import asyncio
import aiohttp
import os
import json

async def check_media_events():
    supabase_url = os.getenv('SUPABASE_URL', 'https://suzxmthipriaglududga.supabase.co')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1enhtdGhpcHJpYWdsdWR1ZGdhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQ2ODUxMiwiZXhwIjoyMDcxMDQ0NTEyfQ.uAF5QDhBXDmI9LdAmeMcJfcc5VTtRT063zmXQShES-A')
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # Get recent messages and check for media
        async with session.get(
            f"{supabase_url}/rest/v1/archived_messages?order=archived_at.desc&limit=20",
            headers=headers
        ) as resp:
            if resp.status == 200:
                messages = await resp.json()
                print(f"Checking {len(messages)} messages for media content...")
                
                media_count = 0
                for msg in messages:
                    content = msg['content']
                    msgtype = content.get('msgtype', 'unknown')
                    
                    # Check for media message types
                    if msgtype in ['m.image', 'm.video', 'm.audio', 'm.file']:
                        media_count += 1
                        print(f"📎 MEDIA FOUND: {msg['event_id']}")
                        print(f"   Type: {msgtype}")
                        print(f"   URL: {content.get('url', 'N/A')}")
                        print(f"   Body: {content.get('body', 'N/A')}")
                        print(f"   Info: {content.get('info', {})}")
                        print()
                    elif 'url' in content and content['url'].startswith('mxc://'):
                        media_count += 1
                        print(f"📎 MXC URL FOUND: {msg['event_id']}")
                        print(f"   Type: {msgtype}")
                        print(f"   URL: {content.get('url')}")
                        print(f"   Body: {content.get('body', 'N/A')}")
                        print()
                
                print(f"Total media messages found: {media_count}")
                
                # Check archived_media table
                async with session.get(
                    f"{supabase_url}/rest/v1/archived_media?limit=10",
                    headers=headers
                ) as resp2:
                    if resp2.status == 200:
                        media_records = await resp2.json()
                        print(f"Media records in archived_media table: {len(media_records)}")
                    else:
                        print("No archived_media table or access issue")
            else:
                error = await resp.text()
                print(f"❌ Failed to get messages: {resp.status} - {error}")

if __name__ == "__main__":
    asyncio.run(check_media_events())