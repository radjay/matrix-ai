#!/usr/bin/env python3
"""Inspect the actual message content to see how media is referenced."""

import asyncio
import aiohttp
import os
import json

async def inspect_recent_messages():
    supabase_url = os.getenv('SUPABASE_URL', 'https://suzxmthipriaglududga.supabase.co')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1enhtdGhpcHJpYWdsdWR1ZGdhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQ2ODUxMiwiZXhwIjoyMDcxMDQ0NTEyfQ.uAF5QDhBXDmI9LdAmeMcJfcc5VTtRT063zmXQShES-A')
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # Get recent media messages
        async with session.get(
            f"{supabase_url}/rest/v1/archived_messages?content->>msgtype=in.(m.image,m.video,m.audio,m.file)&order=archived_at.desc&limit=5",
            headers=headers
        ) as resp:
            if resp.status == 200:
                messages = await resp.json()
                print(f"=== RECENT MEDIA MESSAGES ===")
                
                for msg in messages:
                    print(f"\nEvent: {msg['event_id']}")
                    print(f"Room: {msg['room_id']}")
                    print(f"Sender: {msg['sender']}")
                    print(f"Content structure:")
                    content = msg['content']
                    
                    # Pretty print the content
                    for key, value in content.items():
                        if key == 'info' and isinstance(value, dict):
                            print(f"  {key}:")
                            for info_key, info_value in value.items():
                                print(f"    {info_key}: {info_value}")
                        else:
                            print(f"  {key}: {value}")
                    
                    # Check if there are any alternative URLs or special fields
                    if 'url' in content:
                        url = content['url']
                        print(f"  🔍 MXC URL: {url}")
                        
                        # Check if info contains any special media serving info
                        info = content.get('info', {})
                        if 'thumbnail_url' in info:
                            print(f"  🖼️ Thumbnail URL: {info['thumbnail_url']}")
                        
                        # Look for any bridge-specific fields
                        bridge_fields = [k for k in info.keys() if 'whatsapp' in k.lower() or 'bridge' in k.lower() or 'mautrix' in k.lower()]
                        if bridge_fields:
                            print(f"  🌉 Bridge fields: {bridge_fields}")
                            for field in bridge_fields:
                                print(f"    {field}: {info[field]}")
                    
            else:
                error = await resp.text()
                print(f"❌ Failed to get messages: {resp.status} - {error}")

if __name__ == "__main__":
    asyncio.run(inspect_recent_messages())