#!/usr/bin/env python3
"""Test direct upload to Supabase Storage."""

import asyncio
import aiohttp
import os

async def test_storage_upload():
    supabase_url = os.getenv('SUPABASE_URL', 'https://suzxmthipriaglududga.supabase.co')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1enhtdGhpcHJpYWdsdWR1ZGdhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQ2ODUxMiwiZXhwIjoyMDcxMDQ0NTEyfQ.uAF5QDhBXDmI9LdAmeMcJfcc5VTtRT063zmXQShES-A')
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Check if bucket exists
        print("=== TESTING SUPABASE STORAGE ===")
        
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        async with session.get(f"{supabase_url}/storage/v1/bucket", headers=headers) as resp:
            if resp.status == 200:
                buckets = await resp.json()
                bucket_names = [b.get('name') for b in buckets]
                print(f"✓ Available buckets: {bucket_names}")
                
                if 'matrix-media' in bucket_names:
                    print("✓ matrix-media bucket exists")
                else:
                    print("✗ matrix-media bucket missing")
                    return
            else:
                error = await resp.text()
                print(f"✗ Failed to list buckets: {resp.status} - {error}")
                return
        
        # Test 2: Upload a test file
        print("\n=== TESTING FILE UPLOAD ===")
        test_content = b"This is a test file for Matrix archiver"
        test_filename = "test-upload.txt"
        
        upload_headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "text/plain",
            "x-upsert": "true"
        }
        
        upload_url = f"{supabase_url}/storage/v1/object/matrix-media/{test_filename}"
        print(f"Upload URL: {upload_url}")
        
        async with session.post(upload_url, data=test_content, headers=upload_headers) as resp:
            response_text = await resp.text()
            print(f"Status: {resp.status}")
            print(f"Response: {response_text}")
            
            if resp.status in [200, 201]:
                print("✓ Upload successful!")
                
                # Test 3: List files to confirm
                async with session.get(
                    f"{supabase_url}/storage/v1/object/list/matrix-media",
                    headers=headers
                ) as list_resp:
                    if list_resp.status == 200:
                        files = await list_resp.json()
                        print(f"✓ Files in bucket: {len(files)}")
                        for file in files:
                            print(f"  - {file.get('name')} ({file.get('metadata', {}).get('size', 'unknown')} bytes)")
                    else:
                        print("Could not list files")
                
                # Clean up test file
                async with session.delete(
                    f"{supabase_url}/storage/v1/object/matrix-media/{test_filename}",
                    headers=headers
                ) as del_resp:
                    if del_resp.status in [200, 204]:
                        print("✓ Test file cleaned up")
                    else:
                        print("Failed to clean up test file")
                        
            else:
                print(f"✗ Upload failed: {resp.status}")
                print(f"Headers: {dict(resp.headers)}")
                print(f"Response: {response_text}")

if __name__ == "__main__":
    asyncio.run(test_storage_upload())