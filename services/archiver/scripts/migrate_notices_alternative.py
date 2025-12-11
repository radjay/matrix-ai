#!/usr/bin/env python3
"""Migrate existing notice messages from messages table to notices table - alternative approach."""

import asyncio
import aiohttp
import os
import sys
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_notices():
    """Migrate notice messages from messages table to notices table."""
    
    # Load environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        logger.error("Missing Supabase credentials")
        return False
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Fetch ALL messages and filter in Python (more reliable)
        logger.info("Fetching all messages from messages table...")
        
        all_messages = []
        offset = 0
        limit = 1000
        
        while True:
            async with session.get(
                f"{supabase_url}/rest/v1/messages?select=*&limit={limit}&offset={offset}&order=id.asc",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    logger.error(f"Error fetching messages: {resp.status} - {error}")
                    break
                
                messages = await resp.json()
                if not messages:
                    break
                
                all_messages.extend(messages)
                offset += limit
                
                logger.info(f"Fetched {len(all_messages)} messages so far...")
                
                if len(messages) < limit:
                    break
        
        logger.info(f"Total messages fetched: {len(all_messages)}")
        
        # Step 2: Filter for notice messages
        notice_messages = []
        for msg in all_messages:
            content = msg.get("content", {})
            msgtype = content.get("msgtype", "")
            
            # Check if it's a notice
            if msgtype == "m.notice":
                notice_messages.append(msg)
            elif "fi.mau.bridge_state" in content:
                notice_messages.append(msg)
            else:
                # Check for error indicators in body
                body = content.get("body", "").lower()
                error_indicators = ["not bridged", "failed to bridge", "was not bridged"]
                if any(indicator in body for indicator in error_indicators):
                    notice_messages.append(msg)
        
        logger.info(f"Found {len(notice_messages)} notice messages to migrate")
        
        if not notice_messages:
            logger.info("No notice messages to migrate. Done!")
            return True
        
        # Step 3: Transform and insert into notices table
        logger.info("Migrating notices to notices table...")
        
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        for msg in notice_messages:
            content = msg.get("content", {})
            
            # Determine notice type
            notice_type = "info"
            if "fi.mau.bridge_state" in content:
                notice_type = "bridge_state"
            else:
                body = content.get("body", "").lower()
                if "not bridged" in body or "failed to bridge" in body:
                    notice_type = "error"
                elif "⚠️" in content.get("body", "") or "warning" in body:
                    notice_type = "warning"
            
            # Prepare notice data
            notice_data = {
                "event_id": msg.get("event_id"),
                "room_id": msg.get("room_id"),
                "room_name": msg.get("room_name"),
                "room_display_name": msg.get("room_display_name"),
                "sender": msg.get("sender"),
                "sender_display_name": msg.get("sender_display_name"),
                "timestamp": msg.get("timestamp"),
                "message_type": msg.get("message_type"),
                "content": content,
                "notice_type": notice_type,
                "body": content.get("body", "")
            }
            
            # Insert into notices table
            try:
                async with session.post(
                    f"{supabase_url}/rest/v1/notices",
                    json=notice_data,
                    headers=headers
                ) as resp:
                    if resp.status in [200, 201]:
                        migrated_count += 1
                        if migrated_count % 50 == 0:
                            logger.info(f"Migrated {migrated_count}/{len(notice_messages)} notices...")
                    elif resp.status == 409:
                        # Already exists, skip
                        skipped_count += 1
                        logger.debug(f"Skipped duplicate notice: {notice_data['event_id']}")
                    else:
                        error_text = await resp.text()
                        logger.warning(f"Failed to migrate notice {notice_data['event_id']}: {resp.status} - {error_text}")
                        error_count += 1
            except Exception as e:
                logger.error(f"Error migrating notice {notice_data['event_id']}: {e}")
                error_count += 1
        
        logger.info(f"\nMigration complete!")
        logger.info(f"  Migrated: {migrated_count}")
        logger.info(f"  Skipped (duplicates): {skipped_count}")
        logger.info(f"  Errors: {error_count}")
        
        # Step 4: Delete migrated notices from messages table
        if migrated_count > 0:
            logger.info(f"\nDeleting {migrated_count} notices from messages table...")
            
            # Delete in batches
            batch_size = 100
            deleted_count = 0
            
            for i in range(0, len(notice_messages), batch_size):
                batch = notice_messages[i:i+batch_size]
                event_ids = [msg["event_id"] for msg in batch]
                
                # Delete one by one to avoid URL length issues
                for event_id in event_ids:
                    try:
                        async with session.delete(
                            f"{supabase_url}/rest/v1/messages?event_id=eq.{event_id}",
                            headers={**headers, "Prefer": "return=minimal"}
                        ) as resp:
                            if resp.status in [200, 204]:
                                deleted_count += 1
                            else:
                                error_text = await resp.text()
                                logger.warning(f"Failed to delete {event_id}: {resp.status} - {error_text}")
                    except Exception as e:
                        logger.error(f"Error deleting {event_id}: {e}")
                
                if deleted_count % 50 == 0:
                    logger.info(f"Deleted {deleted_count}/{migrated_count} notices from messages table...")
            
            logger.info(f"Deleted {deleted_count} notices from messages table")
        
        return error_count == 0

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
        logger.error(f"Failed to load environment file: {e}")
        return
    
    success = await migrate_notices()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())


