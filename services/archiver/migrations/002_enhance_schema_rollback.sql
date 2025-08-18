-- Rollback script for Matrix Archiver Schema Enhancements
-- This script reverts the changes made by 002_enhance_schema.sql

BEGIN;

-- Step 1: Drop new triggers
DROP TRIGGER IF EXISTS update_organizations_updated_at ON organizations;
DROP TRIGGER IF EXISTS update_monitored_rooms_updated_at ON monitored_rooms;
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Step 2: Remove new columns from monitored_rooms
ALTER TABLE monitored_rooms DROP COLUMN IF EXISTS organization_id;
ALTER TABLE monitored_rooms DROP COLUMN IF EXISTS auto_join;
ALTER TABLE monitored_rooms DROP COLUMN IF EXISTS archive_media;
ALTER TABLE monitored_rooms DROP COLUMN IF EXISTS updated_at;

-- Step 3: Drop new tables (in reverse dependency order)
DROP TABLE IF EXISTS room_organizations;
DROP TABLE IF EXISTS organizations;

-- Step 4: Remove new columns from messages table
ALTER TABLE messages DROP COLUMN IF EXISTS room_name;
ALTER TABLE messages DROP COLUMN IF EXISTS room_display_name;
ALTER TABLE messages DROP COLUMN IF EXISTS sender_display_name;

-- Step 5: Drop new indexes
DROP INDEX IF EXISTS idx_messages_room_name;
DROP INDEX IF EXISTS idx_messages_sender_display_name;
DROP INDEX IF EXISTS idx_room_organizations_room_id;
DROP INDEX IF EXISTS idx_room_organizations_org_id;
DROP INDEX IF EXISTS idx_monitored_rooms_enabled;
DROP INDEX IF EXISTS idx_monitored_rooms_auto_join;
DROP INDEX IF EXISTS idx_monitored_rooms_org_id;

-- Step 6: Rename tables back to original names
ALTER TABLE messages RENAME TO archived_messages;
ALTER TABLE media RENAME TO archived_media;

-- Step 7: Restore original foreign key constraint
ALTER TABLE archived_media DROP CONSTRAINT IF EXISTS media_event_id_fkey;
ALTER TABLE archived_media ADD CONSTRAINT archived_media_event_id_fkey 
    FOREIGN KEY (event_id) REFERENCES archived_messages(event_id) ON DELETE CASCADE;

-- Step 8: Recreate original indexes
CREATE INDEX idx_messages_room_timestamp ON archived_messages(room_id, timestamp DESC);
CREATE INDEX idx_messages_sender ON archived_messages(sender);
CREATE INDEX idx_media_event_id ON archived_media(event_id);
CREATE INDEX idx_media_storage_path ON archived_media(storage_bucket, storage_path);

-- Step 9: Restore original table comments
COMMENT ON TABLE archived_messages IS 'Archived Matrix messages from monitored rooms';
COMMENT ON TABLE archived_media IS 'Media files from Matrix messages stored in Supabase Storage';
COMMENT ON TABLE monitored_rooms IS 'Configuration for rooms being monitored for archiving';

COMMIT;

-- Verification queries (commented out for safety)
-- SELECT COUNT(*) FROM archived_messages;
-- SELECT COUNT(*) FROM archived_media;
-- SELECT COUNT(*) FROM monitored_rooms;