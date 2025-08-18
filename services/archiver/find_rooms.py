#!/usr/bin/env python3
"""Find all Matrix rooms the archiver bot can see."""

import asyncio
import aiohttp
import os

async def find_all_rooms():
    password = os.getenv('MATRIX_PASSWORD', 'HnvtFkgDZjF4')
    homeserver = "http://localhost:8008"
    
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
                print(f"✓ Bot login successful")
            else:
                error = await resp.text()
                print(f"✗ Login failed: {resp.status} - {error}")
                return
        
        # Get all joined rooms
        async with session.get(
            f"{homeserver}/_matrix/client/r0/joined_rooms",
            params={"access_token": access_token}
        ) as resp:
            if resp.status == 200:
                rooms_data = await resp.json()
                joined_rooms = rooms_data.get("joined_rooms", [])
                print(f"\n🏠 Found {len(joined_rooms)} rooms:")
                
                # Get room details for each
                for room_id in joined_rooms:
                    await get_room_info(session, homeserver, access_token, room_id)
                    
            else:
                error = await resp.text()
                print(f"✗ Failed to get joined rooms: {resp.status} - {error}")

async def get_room_info(session, homeserver, access_token, room_id):
    """Get detailed info about a room."""
    try:
        # Get room state
        async with session.get(
            f"{homeserver}/_matrix/client/r0/rooms/{room_id}/state",
            params={"access_token": access_token}
        ) as resp:
            if resp.status == 200:
                state_events = await resp.json()
                
                # Extract room info
                room_name = None
                room_topic = None
                room_avatar = None
                member_count = 0
                
                for event in state_events:
                    if event.get("type") == "m.room.name":
                        room_name = event.get("content", {}).get("name")
                    elif event.get("type") == "m.room.topic":
                        room_topic = event.get("content", {}).get("topic")
                    elif event.get("type") == "m.room.avatar":
                        room_avatar = event.get("content", {}).get("url")
                    elif event.get("type") == "m.room.member":
                        if event.get("content", {}).get("membership") == "join":
                            member_count += 1
                
                print(f"\n📋 Room ID: {room_id}")
                print(f"   Name: {room_name or 'No name'}")
                print(f"   Topic: {room_topic or 'No topic'}")
                print(f"   Members: {member_count}")
                print(f"   WhatsApp Group: {'Yes' if 'whatsapp' in (room_name or '').lower() or room_id.endswith(':matrix.radx.dev') else 'Maybe'}")
                
            else:
                print(f"   ❌ Could not get info for {room_id}")
                
    except Exception as e:
        print(f"   ❌ Error getting room info: {e}")

if __name__ == "__main__":
    os.environ['MATRIX_PASSWORD'] = 'HnvtFkgDZjF4'
    asyncio.run(find_all_rooms())