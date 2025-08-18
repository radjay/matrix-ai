#!/usr/bin/env python3
"""Check which rooms the archiver bot is in."""

import asyncio
import aiohttp
import os

async def check_bot_rooms():
    # Get credentials
    password = os.getenv('MATRIX_PASSWORD', 'HnvtFkgDZjF4')
    homeserver = "http://localhost:8008"
    
    async with aiohttp.ClientSession() as session:
        # Login to get access token
        login_data = {
            "type": "m.login.password",
            "user": "@archiver:matrix.radx.dev",
            "password": password
        }
        
        async with session.post(f"{homeserver}/_matrix/client/r0/login", json=login_data) as resp:
            if resp.status == 200:
                data = await resp.json()
                access_token = data["access_token"]
                print(f"✓ Bot login successful")
            else:
                error = await resp.text()
                print(f"✗ Login failed: {resp.status} - {error}")
                return
        
        # Check joined rooms
        async with session.get(f"{homeserver}/_matrix/client/r0/joined_rooms", params={"access_token": access_token}) as resp:
            if resp.status == 200:
                rooms_data = await resp.json()
                joined_rooms = rooms_data.get("joined_rooms", [])
                print(f"✓ Bot is in {len(joined_rooms)} rooms:")
                for room in joined_rooms:
                    print(f"  - {room}")
                    
                # Check target rooms
                target_rooms = ["!kAXAqLUxiVymvHdEaT:matrix.radx.dev", "!pNQYyRfhWFNWtDbqei:matrix.radx.dev"]
                for target in target_rooms:
                    if target in joined_rooms:
                        print(f"✓ Bot is in target room: {target}")
                    else:
                        print(f"✗ Bot NOT in target room: {target}")
            else:
                error = await resp.text()
                print(f"✗ Failed to get joined rooms: {resp.status} - {error}")

if __name__ == "__main__":
    os.environ['MATRIX_PASSWORD'] = 'HnvtFkgDZjF4'
    asyncio.run(check_bot_rooms())