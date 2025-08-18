#!/usr/bin/env python3
"""Debug media access methods."""

import asyncio
import aiohttp
import os

async def debug_media_access():
    password = os.getenv('MATRIX_PASSWORD', 'HnvtFkgDZjF4')
    homeserver = "http://localhost:8008"
    
    # Test MXC URL from your recent media
    mxc_url = "mxc://matrix.radx.dev/bzPxwBRBZtSoQrTAevCZwCjr"  # Your new video
    server_name, media_id = mxc_url[6:].split("/", 1)
    
    async with aiohttp.ClientSession() as session:
        # Login first
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
                print(f"✗ Login failed: {resp.status}")
                return
        
        # Test different media download methods
        test_urls = [
            # Standard media API
            f"{homeserver}/_matrix/media/r0/download/{server_name}/{media_id}",
            f"{homeserver}/_matrix/media/v3/download/{server_name}/{media_id}",
            f"{homeserver}/_matrix/media/v1/download/{server_name}/{media_id}",
            
            # With authentication
            f"{homeserver}/_matrix/media/r0/download/{server_name}/{media_id}?access_token={access_token}",
            f"{homeserver}/_matrix/media/v3/download/{server_name}/{media_id}?access_token={access_token}",
            
            # Try thumbnail endpoint (sometimes works when download doesn't)
            f"{homeserver}/_matrix/media/r0/thumbnail/{server_name}/{media_id}?width=800&height=600",
            f"{homeserver}/_matrix/media/r0/thumbnail/{server_name}/{media_id}?width=800&height=600&access_token={access_token}",
        ]
        
        for i, url in enumerate(test_urls):
            print(f"\n{i+1}. Testing: {url[:80]}...")
            
            headers = {}
            if "access_token" not in url:
                headers["Authorization"] = f"Bearer {access_token}"
            
            try:
                async with session.get(url, headers=headers) as resp:
                    print(f"   Status: {resp.status}")
                    print(f"   Content-Type: {resp.headers.get('Content-Type', 'unknown')}")
                    print(f"   Content-Length: {resp.headers.get('Content-Length', 'unknown')}")
                    
                    if resp.status == 200:
                        content_type = resp.headers.get('Content-Type', '')
                        if content_type.startswith(('image/', 'video/', 'audio/')):
                            print(f"   🎉 SUCCESS! Media file accessible")
                            print(f"   Content type: {content_type}")
                            # Read a small portion to verify it's real content
                            content_sample = await resp.read(100)
                            print(f"   Sample bytes: {len(content_sample)} bytes read")
                            break
                        else:
                            response_text = await resp.text()
                            print(f"   Response: {response_text[:200]}")
                    elif resp.status == 404:
                        print(f"   ❌ Not found")
                    elif resp.status == 429:
                        print(f"   ⏱️ Rate limited")
                    else:
                        error = await resp.text()
                        print(f"   ❌ Error: {error[:200]}")
                        
            except Exception as e:
                print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(debug_media_access())