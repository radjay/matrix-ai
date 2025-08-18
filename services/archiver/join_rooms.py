#!/usr/bin/env python3
"""Make archiver bot join the target rooms."""

import asyncio
import aiohttp
import os

async def join_rooms():
    # Get credentials
    password = os.getenv('MATRIX_PASSWORD', 'HnvtFkgDZjF4')
    homeserver = "http://localhost:8008"
    target_rooms = ["!kAXAqLUxiVymvHdEaT:matrix.radx.dev", "!pNQYyRfhWFNWtDbqei:matrix.radx.dev"]
    
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
        
        # Join each target room
        for room_id in target_rooms:
            print(f"Attempting to join room: {room_id}")
            
            async with session.post(
                f"{homeserver}/_matrix/client/r0/rooms/{room_id}/join",
                params={"access_token": access_token},
                json={}
            ) as resp:
                if resp.status in [200, 201]:
                    data = await resp.json()
                    print(f"✓ Successfully joined room: {room_id}")
                else:
                    error = await resp.text()
                    print(f"✗ Failed to join room {room_id}: {resp.status} - {error}")

if __name__ == "__main__":
    os.environ['MATRIX_PASSWORD'] = 'HnvtFkgDZjF4'
    asyncio.run(join_rooms())