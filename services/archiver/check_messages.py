#!/usr/bin/env python3
"""Check messages in Supabase database."""

import asyncio
import aiohttp
import os

async def check_messages():
    supabase_url = os.getenv('SUPABASE_URL', 'https://suzxmthipriaglududga.supabase.co')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1enhtdGhpcHJpYWdsdWR1ZGdhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQ2ODUxMiwiZXhwIjoyMDcxMDQ0NTEyfQ.uAF5QDhBXDmI9LdAmeMcJfcc5VTtRT063zmXQShES-A')
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # Get recent messages
        async with session.get(
            f"{supabase_url}/rest/v1/archived_messages?order=archived_at.desc&limit=10",
            headers=headers
        ) as resp:
            if resp.status == 200:
                messages = await resp.json()
                print(f"✅ Found {len(messages)} messages in Supabase:")
                for msg in messages:
                    print(f"  - {msg['event_id']} in {msg['room_id']} by {msg['sender']}")
                    print(f"    Content: {msg['content'].get('body', 'N/A')[:50]}...")
                    print(f"    Archived: {msg['archived_at']}")
                    print()
            else:
                error = await resp.text()
                print(f"❌ Failed to get messages: {resp.status} - {error}")

if __name__ == "__main__":
    asyncio.run(check_messages())