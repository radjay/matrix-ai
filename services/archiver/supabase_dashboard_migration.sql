-- Migration 002: Schema Enhancement for Matrix Archiver
-- TO BE RUN MANUALLY via Supabase Dashboard SQL Editor
-- 
-- BEFORE RUNNING:
-- 1. Create backup: python3 create_backup.py
-- 2. Stop archiver: sudo systemctl stop matrix-archiver
-- 3. Review this SQL script carefully
-- 
-- TO RUN: Dashboard > SQL Editor > New Query > Paste this script > Run

BEGIN;

-- ==========================================
-- STEP 1: RENAME TABLES
-- ==========================================
ALTER TABLE archived_messages RENAME TO messages;
ALTER TABLE archived_media RENAME TO media;

-- ==========================================
-- STEP 2: UPDATE FOREIGN KEY REFERENCES
-- ==========================================
ALTER TABLE media DROP CONSTRAINT archived_media_event_id_fkey;
ALTER TABLE media ADD CONSTRAINT media_event_id_fkey 
    FOREIGN KEY (event_id) REFERENCES messages(event_id) ON DELETE CASCADE;

-- ==========================================
-- STEP 3: ADD HUMAN-READABLE COLUMNS
-- ==========================================
ALTER TABLE messages ADD COLUMN room_name TEXT;
ALTER TABLE messages ADD COLUMN room_display_name TEXT;
ALTER TABLE messages ADD COLUMN sender_display_name TEXT;

-- ==========================================
-- STEP 4: CREATE ORGANIZATIONS SYSTEM
-- ==========================================
CREATE TABLE organizations (
    id BIGSERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE room_organizations (
    id BIGSERIAL PRIMARY KEY,
    room_id TEXT NOT NULL,
    organization_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(room_id, organization_id)
);

-- ==========================================
-- STEP 5: ENHANCE MONITORED_ROOMS TABLE
-- ==========================================
ALTER TABLE monitored_rooms ADD COLUMN organization_id BIGINT REFERENCES organizations(id);
ALTER TABLE monitored_rooms ADD COLUMN auto_join BOOLEAN DEFAULT TRUE;
ALTER TABLE monitored_rooms ADD COLUMN archive_media BOOLEAN DEFAULT TRUE;
ALTER TABLE monitored_rooms ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();

-- ==========================================
-- STEP 6: CREATE/UPDATE INDEXES
-- ==========================================
-- Drop old indexes (if they exist)
DROP INDEX IF EXISTS idx_messages_room_timestamp;
DROP INDEX IF EXISTS idx_messages_sender;
DROP INDEX IF EXISTS idx_media_event_id;
DROP INDEX IF EXISTS idx_media_storage_path;

-- Create new optimized indexes
CREATE INDEX idx_messages_room_timestamp ON messages(room_id, timestamp DESC);
CREATE INDEX idx_messages_sender ON messages(sender);
CREATE INDEX idx_messages_room_name ON messages(room_name);
CREATE INDEX idx_messages_sender_display_name ON messages(sender_display_name);
CREATE INDEX idx_media_event_id ON media(event_id);
CREATE INDEX idx_media_storage_path ON media(storage_bucket, storage_path);

-- New indexes for organizational features
CREATE INDEX idx_room_organizations_room_id ON room_organizations(room_id);
CREATE INDEX idx_room_organizations_org_id ON room_organizations(organization_id);
CREATE INDEX idx_monitored_rooms_enabled ON monitored_rooms(enabled);
CREATE INDEX idx_monitored_rooms_auto_join ON monitored_rooms(auto_join);
CREATE INDEX idx_monitored_rooms_org_id ON monitored_rooms(organization_id);

-- ==========================================
-- STEP 7: UPDATE TABLE COMMENTS
-- ==========================================
COMMENT ON TABLE messages IS 'Matrix messages from monitored rooms with human-readable metadata';
COMMENT ON TABLE media IS 'Media files from Matrix messages stored in Supabase Storage';
COMMENT ON TABLE monitored_rooms IS 'Configuration for rooms being monitored for archiving with enhanced settings';
COMMENT ON TABLE organizations IS 'Organizations for grouping and managing rooms';
COMMENT ON TABLE room_organizations IS 'Many-to-many relationship between rooms and organizations';

-- Add column comments for new fields
COMMENT ON COLUMN messages.room_name IS 'Human-readable room name from Matrix room state';
COMMENT ON COLUMN messages.room_display_name IS 'Formatted display name for the room';
COMMENT ON COLUMN messages.sender_display_name IS 'Display name of the message sender';
COMMENT ON COLUMN monitored_rooms.organization_id IS 'Optional organization this room belongs to';
COMMENT ON COLUMN monitored_rooms.auto_join IS 'Whether archiver should automatically join this room';
COMMENT ON COLUMN monitored_rooms.archive_media IS 'Whether to archive media files from this room';

-- ==========================================
-- STEP 8: CREATE DEFAULT ORGANIZATION
-- ==========================================
INSERT INTO organizations (name, description) 
VALUES ('Default Organization', 'Default organization for existing rooms') 
ON CONFLICT (name) DO NOTHING;

-- ==========================================
-- STEP 9: CREATE TRIGGERS FOR TIMESTAMPS
-- ==========================================
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

-- ==========================================
-- STEP 10: LINK EXISTING ROOMS TO DEFAULT ORG
-- ==========================================
-- Get the default organization ID and link existing rooms
INSERT INTO room_organizations (room_id, organization_id)
SELECT DISTINCT m.room_id, o.id
FROM messages m
CROSS JOIN organizations o
WHERE o.name = 'Default Organization'
ON CONFLICT (room_id, organization_id) DO NOTHING;

COMMIT;

-- ==========================================
-- VERIFICATION QUERIES
-- ==========================================
-- Run these after the migration to verify success:

-- Check table names
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('messages', 'media', 'organizations', 'room_organizations', 'monitored_rooms')
ORDER BY table_name;

-- Check new columns in messages table
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'messages' 
AND column_name IN ('room_name', 'room_display_name', 'sender_display_name')
ORDER BY column_name;

-- Check organizations created
SELECT * FROM organizations;

-- Check room-organization relationships
SELECT COUNT(*) as room_org_count FROM room_organizations;

-- Check enhanced monitored_rooms
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'monitored_rooms' 
AND column_name IN ('organization_id', 'auto_join', 'archive_media', 'updated_at')
ORDER BY column_name;

-- Check data integrity
SELECT 
    (SELECT COUNT(*) FROM messages) as message_count,
    (SELECT COUNT(*) FROM media) as media_count,
    (SELECT COUNT(*) FROM monitored_rooms) as monitored_rooms_count,
    (SELECT COUNT(*) FROM organizations) as organization_count,
    (SELECT COUNT(*) FROM room_organizations) as room_org_count;