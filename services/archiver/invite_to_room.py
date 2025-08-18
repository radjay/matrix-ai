#!/usr/bin/env python3
"""Invite archiver bot to a new room."""

import asyncio
import aiohttp
import os

async def invite_archiver_to_room(room_id):
    """Invite the archiver bot to a specific room."""
    password = "HnvtFkgDZjF4"  # Use your admin/user password
    homeserver = "http://localhost:8008"
    
    async with aiohttp.ClientSession() as session:
        # Login as admin (you'll need to use your main user account)
        login_data = {
            "type": "m.login.password",
            "user": "@admin:matrix.radx.dev",  # Replace with your main user
            "password": password
        }
        
        print(f"Inviting archiver bot to room: {room_id}")
        
        async with session.post(f"{homeserver}/_matrix/client/r0/login", json=login_data) as resp:
            if resp.status == 200:
                data = await resp.json()
                access_token = data["access_token"]
                print(f"✓ Login successful")
            else:
                error = await resp.text()
                print(f"✗ Login failed: {resp.status} - {error}")
                return False
        
        # Invite the archiver bot
        invite_data = {
            "user_id": "@archiver:matrix.radx.dev"
        }
        
        async with session.post(
            f"{homeserver}/_matrix/client/r0/rooms/{room_id}/invite",
            json=invite_data,
            params={"access_token": access_token}
        ) as resp:
            if resp.status == 200:
                print(f"✓ Successfully invited archiver bot")
                return True
            else:
                error = await resp.text()
                print(f"✗ Failed to invite bot: {resp.status} - {error}")
                return False

if __name__ == "__main__":
    # Replace with your actual new room ID
    new_room_id = input("Enter the new room ID: ")
    asyncio.run(invite_archiver_to_room(new_room_id))