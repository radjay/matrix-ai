#!/usr/bin/env python3
"""Request WhatsApp media files through the bridge."""

import asyncio
import aiohttp
import os

async def request_media_from_bridge():
    """Try to request media through WhatsApp bridge by reacting with recycle emoji."""
    password = os.getenv('MATRIX_PASSWORD', 'HnvtFkgDZjF4')
    homeserver = "http://localhost:8008"
    
    # Media event IDs we want to request
    media_events = [
        "$YJX322SQQgI2EwUTSynzSynHKAQ3rMECFfT8CXrp4EM",  # Image
        "$2tJXe1F6cdxetlMDL4E9Ke5dMgwEnTAJVWbCneEjgV4"   # Video
    ]
    
    async with aiohttp.ClientSession() as session:
        # Login
        login_data = {
            "type": "m.login.password", 
            "user": "@archiver:matrix.radx.dev",
            "password": password
        }
        
        async with session.post(f"{homeserver}/_matrix/client/r0/login", json=login_data) as resp:
            if resp.status == 200:
                data = await resp.json()
                access_token = data["access_token"]
                print(f"✓ Login successful")
            else:
                print(f"✗ Login failed")
                return
        
        # React with recycle emoji to request media
        for event_id in media_events:
            print(f"\nRequesting media for {event_id}...")
            
            # Determine room (try both rooms)
            rooms = ["!pNQYyRfhWFNWtDbqei:matrix.radx.dev", "!kAXAqLUxiVymvHdEaT:matrix.radx.dev"]
            
            for room_id in rooms:
                react_data = {
                    "m.relates_to": {
                        "rel_type": "m.annotation",
                        "event_id": event_id,
                        "key": "♻️"
                    }
                }
                
                async with session.put(
                    f"{homeserver}/_matrix/client/r0/rooms/{room_id}/send/m.reaction/{event_id}_recycle",
                    json=react_data,
                    params={"access_token": access_token}
                ) as resp:
                    if resp.status in [200, 201]:
                        print(f"✓ Sent recycle reaction in {room_id}")
                        break
                    else:
                        print(f"✗ Failed to react in {room_id}: {resp.status}")
        
        print("\n📱 Media requests sent! Check your connected WhatsApp device.")
        print("The bridge should attempt to re-download the media files from your phone.")

if __name__ == "__main__":
    asyncio.run(request_media_from_bridge())