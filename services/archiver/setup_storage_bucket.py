#!/usr/bin/env python3
"""Setup Supabase Storage bucket for Matrix media."""

import asyncio
import aiohttp
import os

async def setup_storage():
    supabase_url = os.getenv('SUPABASE_URL', 'https://suzxmthipriaglududga.supabase.co')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1enhtdGhpcHJpYWdsdWR1ZGdhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQ2ODUxMiwiZXhwIjoyMDcxMDQ0NTEyfQ.uAF5QDhBXDmI9LdAmeMcJfcc5VTtRT063zmXQShES-A')
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # Check if bucket exists
        print("Checking existing buckets...")
        async with session.get(f"{supabase_url}/storage/v1/bucket", headers=headers) as resp:
            if resp.status == 200:
                buckets = await resp.json()
                bucket_names = [b.get('name') for b in buckets]
                print(f"Existing buckets: {bucket_names}")
                
                if 'matrix-media' not in bucket_names:
                    print("Creating matrix-media bucket...")
                    bucket_data = {
                        "id": "matrix-media",
                        "name": "matrix-media",
                        "public": False
                    }
                    
                    async with session.post(
                        f"{supabase_url}/storage/v1/bucket",
                        json=bucket_data,
                        headers=headers
                    ) as create_resp:
                        if create_resp.status in [200, 201]:
                            print("✅ Created matrix-media bucket")
                        else:
                            error = await create_resp.text()
                            print(f"❌ Failed to create bucket: {create_resp.status} - {error}")
                else:
                    print("✅ matrix-media bucket already exists")
            else:
                error = await resp.text()
                print(f"❌ Failed to get buckets: {resp.status} - {error}")

if __name__ == "__main__":
    asyncio.run(setup_storage())