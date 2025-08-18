-- Matrix Archiver Schema Enhancements
-- Phase 1: Database Schema Foundation
-- Removes "archived_" prefix, adds human-readable fields, creates organizations system

BEGIN;

-- Step 1: Rename existing tables (remove "archived_" prefix)
ALTER TABLE archived_messages RENAME TO messages;
ALTER TABLE archived_media RENAME TO media;

-- Step 2: Update foreign key references in media table
ALTER TABLE media DROP CONSTRAINT archived_media_event_id_fkey;
ALTER TABLE media ADD CONSTRAINT media_event_id_fkey 
    FOREIGN KEY (event_id) REFERENCES messages(event_id) ON DELETE CASCADE;

-- Step 3: Add human-readable fields to messages table
ALTER TABLE messages ADD COLUMN room_name TEXT;
ALTER TABLE messages ADD COLUMN room_display_name TEXT;
ALTER TABLE messages ADD COLUMN sender_display_name TEXT;

-- Step 4: Create organizations table
CREATE TABLE organizations (
    id BIGSERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Step 5: Create room-organization relationships table
CREATE TABLE room_organizations (
    id BIGSERIAL PRIMARY KEY,
    room_id TEXT NOT NULL,
    organization_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(room_id, organization_id)
);

-- Step 6: Enhance monitored_rooms table
ALTER TABLE monitored_rooms ADD COLUMN organization_id BIGINT REFERENCES organizations(id);
ALTER TABLE monitored_rooms ADD COLUMN auto_join BOOLEAN DEFAULT TRUE;
ALTER TABLE monitored_rooms ADD COLUMN archive_media BOOLEAN DEFAULT TRUE;
ALTER TABLE monitored_rooms ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();

-- Step 7: Update indexes for new schema
DROP INDEX IF EXISTS idx_messages_room_timestamp;
DROP INDEX IF EXISTS idx_messages_sender;
DROP INDEX IF EXISTS idx_media_event_id;
DROP INDEX IF EXISTS idx_media_storage_path;

-- Recreate indexes with new table names
CREATE INDEX idx_messages_room_timestamp ON messages(room_id, timestamp DESC);
CREATE INDEX idx_messages_sender ON messages(sender);
CREATE INDEX idx_messages_room_name ON messages(room_name);
CREATE INDEX idx_messages_sender_display_name ON messages(sender_display_name);
CREATE INDEX idx_media_event_id ON media(event_id);
CREATE INDEX idx_media_storage_path ON media(storage_bucket, storage_path);

-- Additional indexes for new functionality
CREATE INDEX idx_room_organizations_room_id ON room_organizations(room_id);
CREATE INDEX idx_room_organizations_org_id ON room_organizations(organization_id);
CREATE INDEX idx_monitored_rooms_enabled ON monitored_rooms(enabled);
CREATE INDEX idx_monitored_rooms_auto_join ON monitored_rooms(auto_join);
CREATE INDEX idx_monitored_rooms_org_id ON monitored_rooms(organization_id);

-- Step 8: Update table comments
COMMENT ON TABLE messages IS 'Matrix messages from monitored rooms with human-readable metadata';
COMMENT ON TABLE media IS 'Media files from Matrix messages stored in Supabase Storage';
COMMENT ON TABLE monitored_rooms IS 'Configuration for rooms being monitored for archiving with enhanced settings';
COMMENT ON TABLE organizations IS 'Organizations for grouping and managing rooms';
COMMENT ON TABLE room_organizations IS 'Many-to-many relationship between rooms and organizations';

-- Step 9: Add column comments for new fields
COMMENT ON COLUMN messages.room_name IS 'Human-readable room name from Matrix room state';
COMMENT ON COLUMN messages.room_display_name IS 'Formatted display name for the room';
COMMENT ON COLUMN messages.sender_display_name IS 'Display name of the message sender';
COMMENT ON COLUMN monitored_rooms.organization_id IS 'Optional organization this room belongs to';
COMMENT ON COLUMN monitored_rooms.auto_join IS 'Whether archiver should automatically join this room';
COMMENT ON COLUMN monitored_rooms.archive_media IS 'Whether to archive media files from this room';

-- Step 10: Create a default organization for existing data
INSERT INTO organizations (name, description) 
VALUES ('Default Organization', 'Default organization for existing rooms') 
ON CONFLICT (name) DO NOTHING;

-- Step 11: Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_organizations_updated_at 
    BEFORE UPDATE ON organizations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_monitored_rooms_updated_at 
    BEFORE UPDATE ON monitored_rooms 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Step 12: Update storage policy name references (if needed)
-- Note: Storage policies should continue to work with the same bucket name

COMMIT;

-- Post-migration verification queries (commented out for safety)
-- SELECT COUNT(*) FROM messages;
-- SELECT COUNT(*) FROM media;
-- SELECT COUNT(*) FROM organizations;
-- SELECT COUNT(*) FROM room_organizations;
-- SELECT COUNT(*) FROM monitored_rooms;