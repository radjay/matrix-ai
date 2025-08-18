#!/usr/bin/env python3
"""Test accessing media through WhatsApp bridge directly."""

import asyncio
import aiohttp
import os

async def test_bridge_media():
    # Bridge runs on port 29318
    bridge_url = "http://localhost:29318"
    mxc_url = "mxc://matrix.radx.dev/bzPxwBRBZtSoQrTAevCZwCjr"  # Your recent video
    server_name, media_id = mxc_url[6:].split("/", 1)
    
    async with aiohttp.ClientSession() as session:
        # Test if bridge serves media directly
        test_urls = [
            f"{bridge_url}/_matrix/media/r0/download/{server_name}/{media_id}",
            f"{bridge_url}/_matrix/media/v3/download/{server_name}/{media_id}",
            f"{bridge_url}/media/{media_id}",
            f"{bridge_url}/media/download/{server_name}/{media_id}",
            f"{bridge_url}/_mautrix/media/{media_id}",
        ]
        
        for i, url in enumerate(test_urls):
            print(f"{i+1}. Testing bridge media: {url}")
            try:
                async with session.get(url, timeout=5) as resp:
                    print(f"   Status: {resp.status}")
                    print(f"   Content-Type: {resp.headers.get('Content-Type', 'unknown')}")
                    
                    if resp.status == 200:
                        content_type = resp.headers.get('Content-Type', '')
                        if content_type.startswith(('image/', 'video/')):
                            print(f"   🎉 SUCCESS! Media accessible via bridge")
                            return url
                        else:
                            content = await resp.text()
                            print(f"   Response: {content[:100]}")
                    else:
                        print(f"   ❌ Failed")
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Also check if Element is using federation to get media
        print(f"\n=== CHECKING FEDERATION ACCESS ===")
        federation_url = f"http://localhost:8008/_matrix/federation/v1/media/download/{server_name}/{media_id}"
        try:
            async with session.get(federation_url) as resp:
                print(f"Federation download: {resp.status}")
                if resp.status == 200:
                    print("🎉 Media accessible via federation!")
                    return federation_url
        except Exception as e:
            print(f"Federation error: {e}")
        
        return None

if __name__ == "__main__":
    asyncio.run(test_bridge_media())