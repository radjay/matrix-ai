#!/usr/bin/env python3
"""Make archiver bot join the new room."""

import asyncio
import aiohttp
import os

async def join_new_room():
    password = os.getenv('MATRIX_PASSWORD', 'HnvtFkgDZjF4')
    homeserver = "http://localhost:8008"
    new_room_id = "!qiOVKPJqIaevqYiPfv:matrix.radx.dev"
    
    async with aiohttp.ClientSession() as session:
        # Login as archiver bot
        login_data = {
            "type": "m.login.password",
            "user": "@archiver:matrix.radx.dev",
            "password": password
        }
        
        async with session.post(f"{homeserver}/_matrix/client/r0/login", json=login_data) as resp:
            if resp.status == 200:
                data = await resp.json()
                access_token = data["access_token"]
                print(f"✓ Archiver bot login successful")
            else:
                error = await resp.text()
                print(f"✗ Login failed: {resp.status} - {error}")
                return
        
        # Join the new room
        print(f"Joining room: {new_room_id}")
        
        async with session.post(
            f"{homeserver}/_matrix/client/r0/rooms/{new_room_id}/join",
            params={"access_token": access_token},
            json={}
        ) as resp:
            if resp.status in [200, 201]:
                print(f"✓ Successfully joined room: {new_room_id}")
            else:
                error = await resp.text()
                print(f"✗ Failed to join room: {resp.status} - {error}")
                print("The bot might need to be invited first by a room member")
        
        # Verify the bot is now in all 3 rooms
        async with session.get(
            f"{homeserver}/_matrix/client/r0/joined_rooms",
            params={"access_token": access_token}
        ) as resp:
            if resp.status == 200:
                rooms_data = await resp.json()
                joined_rooms = rooms_data.get("joined_rooms", [])
                print(f"\n✓ Archiver bot is now in {len(joined_rooms)} rooms:")
                for room in joined_rooms:
                    print(f"  - {room}")
            else:
                print("Failed to verify room membership")

if __name__ == "__main__":
    asyncio.run(join_new_room())