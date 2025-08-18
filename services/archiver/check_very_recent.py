#!/usr/bin/env python3
"""Check for very recent messages (last few minutes)."""

import asyncio
import aiohttp
import os
from datetime import datetime, timezone, timedelta

async def check_very_recent():
    supabase_url = os.getenv('SUPABASE_URL', 'https://suzxmthipriaglududga.supabase.co')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1enhtdGhpcHJpYWdsdWR1ZGdhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQ2ODUxMiwiZXhwIjoyMDcxMDQ0NTEyfQ.uAF5QDhBXDmI9LdAmeMcJfcc5VTtRT063zmXQShES-A')
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    # Check for messages in last 10 minutes
    ten_minutes_ago = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
    
    async with aiohttp.ClientSession() as session:
        # Get very recent messages
        async with session.get(
            f"{supabase_url}/rest/v1/archived_messages?archived_at=gte.{ten_minutes_ago}&order=archived_at.desc&limit=10",
            headers=headers
        ) as resp:
            if resp.status == 200:
                messages = await resp.json()
                print(f"=== MESSAGES IN LAST 10 MINUTES ===")
                print(f"Found {len(messages)} recent messages:")
                
                for msg in messages:
                    content = msg['content']
                    has_media = content.get('url', '').startswith('mxc://')
                    print(f"\n⏰ {msg['archived_at']}")
                    print(f"   Event: {msg['event_id']}")
                    print(f"   Room: {msg['room_id']}")
                    print(f"   Type: {content.get('msgtype', 'unknown')}")
                    print(f"   Body: {content.get('body', 'N/A')[:50]}...")
                    print(f"   Media: {'✓' if has_media else '✗'}")
                    if has_media:
                        print(f"   MXC: {content.get('url')}")
                
                if not messages:
                    print("❌ No messages found in last 10 minutes")
                    print("This suggests the WhatsApp message hasn't been bridged yet")
            else:
                error = await resp.text()
                print(f"❌ Failed to get recent messages: {resp.status} - {error}")

if __name__ == "__main__":
    asyncio.run(check_very_recent())