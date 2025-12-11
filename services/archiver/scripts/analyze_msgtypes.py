#!/usr/bin/env python3
"""Analyze msgtypes in messages table to determine what should go to notices."""

import asyncio
import aiohttp
import os
import json
from collections import Counter

async def analyze_msgtypes():
    """Analyze all msgtypes in the messages table."""
    
    # Load environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("Missing Supabase credentials")
        return
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    msgtypes = Counter()
    notice_samples = []
    other_samples = []
    
    async with aiohttp.ClientSession() as session:
        # Get messages in batches
        offset = 0
        limit = 1000
        total_fetched = 0
        
        while True:
            async with session.get(
                f"{supabase_url}/rest/v1/messages?select=content,message_type&limit={limit}&offset={offset}",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    print(f"Error fetching messages: {resp.status} - {error}")
                    break
                
                messages = await resp.json()
                if not messages:
                    break
                
                for msg in messages:
                    content = msg.get("content", {})
                    msgtype = content.get("msgtype")
                    message_type = msg.get("message_type")
                    
                    if msgtype:
                        msgtypes[msgtype] += 1
                        
                        # Collect samples
                        if msgtype == "m.notice":
                            if len(notice_samples) < 10:
                                notice_samples.append({
                                    "msgtype": msgtype,
                                    "body": content.get("body", "")[:100],
                                    "has_bridge_state": "fi.mau.bridge_state" in content,
                                    "content_keys": list(content.keys())[:10]
                                })
                        else:
                            if len(other_samples) < 5:
                                other_samples.append({
                                    "msgtype": msgtype,
                                    "body": content.get("body", "")[:100] if content.get("body") else None,
                                    "content_keys": list(content.keys())[:10]
                                })
                
                total_fetched += len(messages)
                offset += limit
                
                # Limit to first 10000 messages for analysis
                if total_fetched >= 10000 or len(messages) < limit:
                    break
    
    print("=" * 70)
    print("MSG TYPE ANALYSIS")
    print("=" * 70)
    print(f"\nTotal messages analyzed: {total_fetched}")
    print(f"\nUnique msgtypes found: {len(msgtypes)}")
    print("\nMsgtype distribution:")
    print("-" * 70)
    for msgtype, count in msgtypes.most_common():
        percentage = (count / total_fetched) * 100
        print(f"  {msgtype:20} {count:6} ({percentage:5.1f}%)")
    
    print("\n" + "=" * 70)
    print("NOTICE MESSAGE SAMPLES")
    print("=" * 70)
    for i, sample in enumerate(notice_samples, 1):
        print(f"\nSample {i}:")
        print(f"  Body: {sample['body']}")
        print(f"  Has bridge_state: {sample['has_bridge_state']}")
        print(f"  Content keys: {sample['content_keys']}")
    
    print("\n" + "=" * 70)
    print("OTHER MSG TYPE SAMPLES")
    print("=" * 70)
    for i, sample in enumerate(other_samples, 1):
        print(f"\nSample {i}:")
        print(f"  Msgtype: {sample['msgtype']}")
        if sample['body']:
            print(f"  Body: {sample['body']}")
        print(f"  Content keys: {sample['content_keys']}")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    
    if "m.notice" in msgtypes:
        print(f"\n✓ m.notice messages ({msgtypes['m.notice']} found) should go to notices table")
        print("  - These include bridge state updates, error messages, and system notices")
    
    # Check for other potential notice types
    potential_notices = []
    for msgtype in msgtypes:
        if msgtype and ("error" in msgtype.lower() or "notice" in msgtype.lower() or "warning" in msgtype.lower()):
            if msgtype != "m.notice":
                potential_notices.append(msgtype)
    
    if potential_notices:
        print(f"\n⚠ Potential notice types found: {', '.join(potential_notices)}")
    else:
        print("\n✓ No other obvious notice/error msgtypes found")
    
    print("\n✓ Regular message types (m.text, m.image, m.video, m.file, m.emote) should stay in messages table")

async def main():
    """Main entry point."""
    # Load environment from env file
    env_file = "/home/matrix-ai/services/archiver/config/env"
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip('"\'')
                    os.environ[key] = value
    except Exception as e:
        print(f"Failed to load environment file: {e}")
        return
    
    await analyze_msgtypes()

if __name__ == "__main__":
    asyncio.run(main())


