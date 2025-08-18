# Matrix Archiver Improvements - PRD v2.0

## Overview
This PRD outlines incremental improvements to the Matrix archiver to enhance usability, organization, and dynamic room management. The focus is on making archived data more human-readable and adding organizational capabilities.

## Current State Analysis

### Database Schema (Current)
- `archived_messages` - stores Matrix messages with Matrix IDs only
- `archived_media` - stores media files linked to messages  
- `monitored_rooms` - exists but currently unused by archiver

### Archiver Implementation (Current)
- `simple_archiver.py` - hardcoded to join all rooms automatically
- No dynamic room management from database
- Stores raw Matrix IDs without human-readable names

## Proposed Improvements

### 1. Database Schema Enhancements

#### 1.1 Remove "archived_" Prefix
**Current:** `archived_messages`, `archived_media`
**Proposed:** `messages`, `media`

**Rationale:** Simpler naming since all data in this system is archived by definition.

#### 1.2 Add Human-Readable Fields

**Messages Table Updates:**
```sql
ALTER TABLE messages ADD COLUMN room_name TEXT;
ALTER TABLE messages ADD COLUMN room_display_name TEXT;
ALTER TABLE messages ADD COLUMN sender_display_name TEXT;
```

**Fields to Add:**
- `room_name` - Matrix room name (e.g., "Engineering Team")
- `room_display_name` - Formatted display name from room state
- `sender_display_name` - User's display name (e.g., "John Smith")

**Note:** Keep existing `room_id` and `sender` fields for technical operations.

#### 1.3 Organizations System

**New Tables:**
```sql
-- Organizations table
CREATE TABLE organizations (
    id BIGSERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Room-Organization relationships
CREATE TABLE room_organizations (
    id BIGSERIAL PRIMARY KEY,
    room_id TEXT NOT NULL,
    organization_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(room_id, organization_id)
);
```

### 2. Dynamic Room Management

#### 2.1 Monitored Rooms Enhancement
**Current:** Table exists but unused
**Proposed:** Active room management from database

**Enhanced Schema:**
```sql
ALTER TABLE monitored_rooms ADD COLUMN organization_id BIGINT REFERENCES organizations(id);
ALTER TABLE monitored_rooms ADD COLUMN auto_join BOOLEAN DEFAULT TRUE;
ALTER TABLE monitored_rooms ADD COLUMN archive_media BOOLEAN DEFAULT TRUE;
```

#### 2.2 Archiver Integration
- Read monitored rooms from `monitored_rooms` table on startup
- Periodic refresh of monitored rooms (every 5 minutes)
- Auto-join rooms marked with `auto_join = TRUE`
- Skip rooms marked with `enabled = FALSE`

### 3. Implementation Plan

#### Phase 1: Database Migration
- Create migration script for schema changes
- Rename tables (`archived_*` → clean names)
- Add human-readable columns
- Create organizations tables

#### Phase 2: Room Name Resolution
- Add Matrix API calls to resolve room names
- Add Matrix API calls to resolve user display names
- Update archiver to populate human-readable fields
- Backfill existing records with resolved names

#### Phase 3: Dynamic Room Management
- Modify archiver to read from `monitored_rooms` table
- Add periodic refresh mechanism
- Implement room joining/leaving based on database changes
- Add logging for room management actions

#### Phase 4: Organizations Integration
- Add organization assignment for existing rooms
- Update queries to filter by organization
- Add organization-based data export capabilities

### 4. Technical Specifications

#### 4.1 API Enhancements
**Room Name Resolution:**
```python
async def resolve_room_name(self, room_id: str) -> tuple[str, str]:
    """Returns (room_name, display_name) from Matrix room state."""
```

**User Display Name Resolution:**
```python
async def resolve_user_display_name(self, user_id: str, room_id: str) -> str:
    """Returns user's display name in the context of a room."""
```

#### 4.2 Database Schema Migration
```sql
-- Migration: 002_enhance_schema.sql
BEGIN;

-- Rename tables
ALTER TABLE archived_messages RENAME TO messages;
ALTER TABLE archived_media RENAME TO media;

-- Add human-readable fields
ALTER TABLE messages ADD COLUMN room_name TEXT;
ALTER TABLE messages ADD COLUMN room_display_name TEXT;
ALTER TABLE messages ADD COLUMN sender_display_name TEXT;

-- Create organizations
CREATE TABLE organizations (
    id BIGSERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create room-organization relationships
CREATE TABLE room_organizations (
    id BIGSERIAL PRIMARY KEY,
    room_id TEXT NOT NULL,
    organization_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(room_id, organization_id)
);

-- Enhance monitored_rooms
ALTER TABLE monitored_rooms ADD COLUMN organization_id BIGINT REFERENCES organizations(id);
ALTER TABLE monitored_rooms ADD COLUMN auto_join BOOLEAN DEFAULT TRUE;
ALTER TABLE monitored_rooms ADD COLUMN archive_media BOOLEAN DEFAULT TRUE;

COMMIT;
```

#### 4.3 Configuration Changes
**Environment Variables:**
- `ROOM_REFRESH_INTERVAL_MINUTES=5` - How often to check for new rooms
- `AUTO_JOIN_ENABLED=true` - Whether to auto-join new monitored rooms

### 5. Benefits

#### 5.1 Improved Data Usability
- Room names instead of cryptic Matrix IDs
- User display names for better message attribution
- Organization-based data segmentation

#### 5.2 Operational Improvements
- No archiver restart required for room changes
- Database-driven room management
- Better troubleshooting with Matrix IDs preserved

#### 5.3 Scalability
- Organization-based data filtering
- Centralized room configuration
- Automated room joining workflow

### 6. Migration Strategy

#### 6.1 Backward Compatibility
- Keep all existing Matrix ID fields
- Gradual rollout with feature flags
- Fallback to Matrix IDs when names unavailable

#### 6.2 Data Backfill
- Script to resolve names for existing messages
- Rate-limited Matrix API calls to avoid throttling
- Progress tracking for large datasets

### 7. Success Metrics

#### 7.1 Usability
- 95% of messages have resolved room and user names
- Sub-1 minute room addition without restart
- Organization-based queries return results <2s

#### 7.2 Reliability
- No message loss during migration
- 99.9% archiver uptime during dynamic room changes
- Successful auto-join rate >95%

## Next Steps

1. Review and approve PRD
2. Create detailed implementation tickets
3. Develop and test migration scripts
4. Implement Phase 1 (database changes)
5. Roll out incrementally with monitoring

## Appendix: Example Queries

**Before (Current):**
```sql
SELECT * FROM archived_messages WHERE room_id = '!abcd1234:matrix.org';
```

**After (Improved):**
```sql
-- More readable query
SELECT room_name, sender_display_name, content 
FROM messages 
WHERE room_name = 'Engineering Team';

-- Organization-based filtering
SELECT m.* FROM messages m
JOIN room_organizations ro ON m.room_id = ro.room_id
JOIN organizations o ON ro.organization_id = o.id
WHERE o.name = 'ACME Corp';
```