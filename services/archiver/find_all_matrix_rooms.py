#!/usr/bin/env python3
"""Find all Matrix rooms on the server (as admin user)."""

import asyncio
import aiohttp
import os

async def find_all_server_rooms():
    password = "HnvtFkgDZjF4"  # admin password
    homeserver = "http://localhost:8008"
    
    async with aiohttp.ClientSession() as session:
        # Login as admin
        login_data = {
            "type": "m.login.password",
            "user": "@admin:matrix.radx.dev", 
            "password": password
        }
        
        async with session.post(f"{homeserver}/_matrix/client/r0/login", json=login_data) as resp:
            if resp.status == 200:
                data = await resp.json()
                access_token = data["access_token"]
                print(f"✓ Admin login successful")
            else:
                error = await resp.text()
                print(f"✗ Login failed: {resp.status} - {error}")
                return
        
        # Get public rooms (this will show bridged rooms)
        async with session.get(
            f"{homeserver}/_matrix/client/r0/publicRooms",
            params={"access_token": access_token, "limit": 100}
        ) as resp:
            if resp.status == 200:
                rooms_data = await resp.json()
                rooms = rooms_data.get("chunk", [])
                print(f"\n🌐 Found {len(rooms)} public rooms:")
                
                for room in rooms:
                    room_id = room.get("room_id")
                    name = room.get("name", "No name")
                    topic = room.get("topic", "")
                    members = room.get("num_joined_members", 0)
                    
                    # Check if it looks like a WhatsApp room
                    is_whatsapp = (
                        "whatsapp" in name.lower() or 
                        any(word in topic.lower() for word in ["whatsapp", "wa", "group"]) or
                        room_id.endswith(":matrix.radx.dev")
                    )
                    
                    print(f"\n📋 Room ID: {room_id}")
                    print(f"   Name: {name}")
                    print(f"   Topic: {topic}")
                    print(f"   Members: {members}")
                    print(f"   WhatsApp: {'✓' if is_whatsapp else '?'}")
                    
            else:
                error = await resp.text()
                print(f"✗ Failed to get public rooms: {resp.status} - {error}")

if __name__ == "__main__":
    asyncio.run(find_all_server_rooms())