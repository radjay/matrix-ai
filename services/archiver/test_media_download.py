#!/usr/bin/env python3
"""Test Matrix media download with authentication."""

import asyncio
import aiohttp
import os

async def test_media_download():
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
                print(f"✓ Login successful")
            else:
                print(f"✗ Login failed")
                return
        
        # Test media download URLs
        mxc_url = "mxc://matrix.radx.dev/bWbmFFVYaZiMsLCwatqLPcDx"
        server_name, media_id = mxc_url[6:].split("/", 1)
        
        test_urls = [
            f"{homeserver}/_matrix/media/r0/download/{server_name}/{media_id}",
            f"{homeserver}/_matrix/media/v3/download/{server_name}/{media_id}",
            f"{homeserver}/_matrix/media/r0/download/{server_name}/{media_id}?access_token={access_token}",
            f"{homeserver}/_matrix/media/v3/download/{server_name}/{media_id}?access_token={access_token}",
        ]
        
        for url in test_urls:
            print(f"\nTesting: {url[:100]}...")
            async with session.get(url) as resp:
                print(f"Status: {resp.status}")
                if resp.status == 200:
                    content_type = resp.headers.get('Content-Type', 'unknown')
                    content_length = resp.headers.get('Content-Length', 'unknown')
                    print(f"✓ SUCCESS! Content-Type: {content_type}, Length: {content_length}")
                    break
                else:
                    error = await resp.text()
                    print(f"Error: {error[:200]}")

if __name__ == "__main__":
    asyncio.run(test_media_download())