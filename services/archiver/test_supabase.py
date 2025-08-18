#!/usr/bin/env python3
"""Test Supabase connection and API access."""

import asyncio
import aiohttp
import os
import json

async def test_supabase():
    # Get credentials
    supabase_url = os.getenv('SUPABASE_URL', '')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
    
    print(f"Supabase URL: {supabase_url}")
    print(f"Supabase key length: {len(supabase_key)} chars")
    
    if not supabase_url or not supabase_key:
        print("✗ Missing Supabase credentials")
        return
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Check table exists
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        print("\n1. Testing table access...")
        async with session.get(
            f"{supabase_url}/rest/v1/archived_messages?limit=1",
            headers=headers
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"✓ Table accessible, found {len(data)} existing messages")
            else:
                error = await resp.text()
                print(f"✗ Table access failed: {resp.status} - {error}")
                return
        
        # Test 2: Insert test message
        print("\n2. Testing message insertion...")
        test_message = {
            "event_id": "$test123:matrix.radx.dev",
            "room_id": "!kAXAqLUxiVymvHdEaT:matrix.radx.dev",
            "sender": "@archiver:matrix.radx.dev", 
            "timestamp": 1755465588000,
            "message_type": "m.room.message",
            "content": {"msgtype": "m.text", "body": "Test message from archiver"}
        }
        
        async with session.post(
            f"{supabase_url}/rest/v1/archived_messages",
            json=test_message,
            headers=headers
        ) as resp:
            if resp.status in [200, 201]:
                print("✓ Test message inserted successfully")
            else:
                error = await resp.text()
                print(f"✗ Test message insertion failed: {resp.status} - {error}")
                print(f"Response: {error}")
        
        # Test 3: Check if test message exists
        print("\n3. Verifying test message...")
        async with session.get(
            f"{supabase_url}/rest/v1/archived_messages?event_id=eq.$test123:matrix.radx.dev",
            headers=headers
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data:
                    print(f"✓ Test message found in database")
                    # Clean up
                    await session.delete(
                        f"{supabase_url}/rest/v1/archived_messages?event_id=eq.$test123:matrix.radx.dev",
                        headers=headers
                    )
                    print("✓ Test message cleaned up")
                else:
                    print("✗ Test message not found")
            else:
                error = await resp.text()
                print(f"✗ Failed to query test message: {resp.status} - {error}")

if __name__ == "__main__":
    os.environ['SUPABASE_URL'] = 'https://suzxmthipriaglududga.supabase.co'
    os.environ['SUPABASE_SERVICE_ROLE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1enhtdGhpcHJpYWdsdWR1ZGdhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQ2ODUxMiwiZXhwIjoyMDcxMDQ0NTEyfQ.uAF5QDhBXDmI9LdAmeMcJfcc5VTtRT063zmXQShES-A'
    asyncio.run(test_supabase())