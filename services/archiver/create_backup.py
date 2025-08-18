#!/usr/bin/env python3
"""
Create complete backup of Matrix archiver database.
Includes both schema documentation and data via REST API.
"""

import asyncio
import aiohttp
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Current schema based on 001_initial_schema.sql
CURRENT_SCHEMA = """
-- Current Schema (Pre-Migration) - From 001_initial_schema.sql
-- This represents the state BEFORE migration 002_enhance_schema.sql

-- Messages table
CREATE TABLE archived_messages (
    id BIGSERIAL PRIMARY KEY,
    event_id TEXT UNIQUE NOT NULL,
    room_id TEXT NOT NULL,
    sender TEXT NOT NULL,
    timestamp BIGINT NOT NULL,
    message_type TEXT NOT NULL,
    content JSONB NOT NULL,
    thread_id TEXT,
    reply_to_event_id TEXT,
    edited_at TIMESTAMPTZ,
    redacted BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMPTZ DEFAULT NOW()
);

-- Media files table (linked to messages via event_id)
CREATE TABLE archived_media (
    id BIGSERIAL PRIMARY KEY,
    event_id TEXT NOT NULL REFERENCES archived_messages(event_id) ON DELETE CASCADE,
    media_type TEXT NOT NULL,
    original_filename TEXT,
    file_size BIGINT,
    mime_type TEXT,
    matrix_url TEXT NOT NULL,
    storage_bucket TEXT NOT NULL DEFAULT 'matrix-media',
    storage_path TEXT NOT NULL,
    public_url TEXT NOT NULL,
    archived_at TIMESTAMPTZ DEFAULT NOW()
);

-- Room configuration table
CREATE TABLE monitored_rooms (
    id BIGSERIAL PRIMARY KEY,
    room_id TEXT UNIQUE NOT NULL,
    room_name TEXT,
    room_alias TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    last_sync_token TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_messages_room_timestamp ON archived_messages(room_id, timestamp DESC);
CREATE INDEX idx_messages_sender ON archived_messages(sender);
CREATE INDEX idx_media_event_id ON archived_media(event_id);
CREATE INDEX idx_media_storage_path ON archived_media(storage_bucket, storage_path);

-- Comments for documentation
COMMENT ON TABLE archived_messages IS 'Archived Matrix messages from monitored rooms';
COMMENT ON TABLE archived_media IS 'Media files from Matrix messages stored in Supabase Storage';
COMMENT ON TABLE monitored_rooms IS 'Configuration for rooms being monitored for archiving';
"""

async def create_complete_backup():
    """Create backup with both schema and data."""
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        logger.error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")
        return False
    
    # Set backup directory
    backup_dir = Path(__file__).parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    # Create timestamped backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"complete_backup_{timestamp}.json"
    
    logger.info(f"Creating complete backup: {backup_file}")
    
    try:
        backup_data = {
            'schema': {
                'description': 'Current database schema before migration',
                'sql': CURRENT_SCHEMA,
                'tables': ['archived_messages', 'archived_media', 'monitored_rooms']
            },
            'data': {},
            'metadata': {
                'backup_timestamp': datetime.now().isoformat(),
                'backup_method': 'complete_schema_and_data',
                'pre_migration': True
            }
        }
        
        # Set up HTTP session
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            logger.info("Connected to Supabase REST API")
            
            # Tables to backup (try both old and new names)
            tables_to_try = [
                ('archived_messages', 'messages'),
                ('archived_media', 'media'),
                ('monitored_rooms', 'monitored_rooms'),
                ('organizations', 'organizations'),
                ('room_organizations', 'room_organizations')
            ]
            
            for old_name, new_name in tables_to_try:
                # Try the new name first, then old name
                for table_name in [new_name, old_name]:
                    if table_name in backup_data['data']:
                        continue  # Already backed up
                    
                    logger.info(f"Trying to backup: {table_name}")
                    
                    try:
                        # Get all data from table
                        async with session.get(
                            f"{supabase_url}/rest/v1/{table_name}",
                            headers=headers
                        ) as resp:
                            if resp.status == 200:
                                table_data = await resp.json()
                                backup_data['data'][old_name] = table_data  # Store with consistent key
                                logger.info(f"✅ Backed up {len(table_data)} records from {table_name}")
                                break  # Success, don't try the other name
                            elif resp.status == 404:
                                logger.debug(f"Table {table_name} not found")
                                continue  # Try the other name
                            else:
                                error = await resp.text()
                                logger.warning(f"Failed to backup {table_name}: {resp.status} - {error}")
                                continue
                                
                    except Exception as e:
                        logger.warning(f"Error trying {table_name}: {e}")
                        continue
                
                # If we get here and no data was backed up, record empty
                if old_name not in backup_data['data']:
                    backup_data['data'][old_name] = []
                    logger.info(f"⚠ No data found for {old_name} (tried {new_name} and {old_name})")
            
            # Add sample data structure for reference
            if backup_data['data']['archived_messages']:
                sample_message = backup_data['data']['archived_messages'][0]
                backup_data['schema']['sample_structures'] = {
                    'archived_messages': {
                        'columns': list(sample_message.keys()),
                        'sample_record': sample_message
                    }
                }
            
            if backup_data['data']['archived_media']:
                sample_media = backup_data['data']['archived_media'][0]
                backup_data['schema']['sample_structures']['archived_media'] = {
                    'columns': list(sample_media.keys()),
                    'sample_record': sample_media
                }
            
            # Write backup file
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            logger.info(f"Complete backup created: {backup_file}")
            
            # Print summary
            total_records = sum(len(data) if isinstance(data, list) else 0 for data in backup_data['data'].values())
            logger.info(f"Backup summary:")
            logger.info(f"  - Schema: Current structure documented")
            logger.info(f"  - Data: {total_records} total records")
            logger.info(f"  - Tables: {', '.join(backup_data['schema']['tables'])}")
            
            return str(backup_file)
            
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return None

async def main():
    """Main entry point."""
    backup_file = await create_complete_backup()
    if backup_file:
        logger.info(f"✅ Complete backup successful: {backup_file}")
        print(f"SUCCESS: {backup_file}")
        sys.exit(0)
    else:
        logger.error("❌ Complete backup failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())