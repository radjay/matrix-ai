# PRD: Matrix Message and Media Archiving to Supabase

## Overview

Simple automated system to archive all Matrix room messages and media files to Supabase for backup and long-term storage.

## Context

Building on our Matrix AI Server infrastructure with:
- Synapse homeserver (localhost:8008)
- Supabase PRO account (PostgreSQL + Storage)
- WhatsApp bridge for multi-platform messaging

## Objectives

### Primary Goals
- Archive all Matrix room messages to Supabase PostgreSQL
- Download and store media files to Supabase Storage
- Preserve chat history independently of Matrix server retention

### Success Metrics
- 100% message capture rate from monitored rooms
- <5 second latency for new message archiving
- 99.9% system uptime
- Complete media preservation with metadata

## Features

### Core Functionality

#### 1. Matrix Room Monitoring
- Monitor specified Matrix rooms for new messages
- Support for multiple room types (public, private, encrypted)
- Real-time event processing via Matrix /sync API
- Historical message backfill for existing rooms

#### 2. Message Archiving
- Store complete message metadata and content
- Preserve message relationships (replies, threads, reactions)
- Handle message edits and redactions
- Support all Matrix message types (text, emotes, notices)

#### 3. Media Processing
- Detect media attachments (images, videos, audio, files) in messages
- Download from Matrix media repository
- Upload to Supabase Storage
- Store media metadata and URLs linked to the original message via event_id
- Maintain referential integrity between messages and their media files

#### 4. Supabase Database Schema
```sql
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
```

#### 5. Configuration Management
- Environment-based configuration
- Room monitoring enable/disable
- Supabase connection settings

## Technical Implementation

### Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Matrix        │    │   Archiving      │    │      Supabase       │
│   Homeserver    │◄──►│   Service        │◄──►│  ┌─────────────────┐│
│   (Synapse)     │    │                  │    │  │   PostgreSQL    ││
└─────────────────┘    └──────────────────┘    │  └─────────────────┘│
                                               │  ┌─────────────────┐│
                                               │  │   Storage       ││
                                               │  └─────────────────┘│
                                               └─────────────────────┘
```

### Technology Stack
- **Language**: Python 3.11+ (async/await support)
- **Matrix SDK**: matrix-nio (async Python client)
- **Database**: Supabase PostgreSQL
- **Storage**: Supabase Storage
- **Framework**: FastAPI + Supabase Python SDK
- **Deployment**: Docker container with systemd service

### File Structure
```
/home/matrix-ai/
├── services/
│   └── archiver/
│       ├── src/
│       │   ├── archiver/
│       │   │   ├── __init__.py
│       │   │   ├── matrix_client.py
│       │   │   ├── supabase_client.py
│       │   │   ├── media_handler.py
│       │   │   ├── config.py
│       │   │   └── main.py
│       │   └── tests/
│       ├── migrations/
│       │   └── 001_initial_schema.sql
│       ├── config/
│       │   └── archiver.yaml
│       ├── Dockerfile
│       ├── requirements.txt
│       └── README.md
└── config/
    └── archiver/
        └── config.yaml
```

### Development Phases

#### Phase 1: Core Archiving (1 week)
1. Supabase project setup and schema migration
2. Matrix client authentication and room joining
3. Message sync to Supabase PostgreSQL
4. Media file download and upload to Supabase Storage
5. Configuration system

#### Phase 2: Enhanced Features (1 week)
1. Historical message backfill
2. Message edit/redaction handling
3. Error handling and retry logic
4. Monitoring and logging
5. Service deployment

## Configuration

### Environment Variables
```yaml
# Matrix connection
matrix:
  homeserver_url: "http://localhost:8008"
  username: "@archiver:matrix.radx.dev"
  password: "${ARCHIVER_PASSWORD}"
  device_name: "Supabase Matrix Archiver"

# Supabase configuration
supabase:
  url: "${SUPABASE_URL}"
  service_role_key: "${SUPABASE_SERVICE_ROLE_KEY}"
  anon_key: "${SUPABASE_ANON_KEY}"
  jwt_secret: "${SUPABASE_JWT_SECRET}"
  # Storage bucket configuration
  storage:
    bucket: "matrix-media"
    public_bucket: true
    file_size_limit: "100MB"
    allowed_mime_types: 
      - "image/*"
      - "video/*"
      - "audio/*"
      - "application/pdf"
      - "text/*"
  # Database connection settings
  database:
    connection_string: "${SUPABASE_DB_URL}"
    pool_size: 10
    max_overflow: 20

# Room monitoring configuration
rooms:
  - room_id: "!example:matrix.radx.dev"
    enabled: true
    backfill: true
  - room_id: "!whatsapp_bridge:matrix.radx.dev"
    enabled: true
    backfill: false

# Processing configuration
processing:
  max_file_size: "100MB"
  batch_size: 50
  sync_timeout: 30000
  concurrent_uploads: 5
  retry_attempts: 3
  retry_delay: 5
```

## Deployment

### Service Setup
```bash
# Install service
sudo cp services/archiver/matrix-archiver.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable matrix-archiver
sudo systemctl start matrix-archiver

# Monitor logs
journalctl -u matrix-archiver -f
```

### Integration with Existing Setup
- Connect to existing Synapse homeserver
- Coordinate with WhatsApp bridge for room monitoring
- Use systemd for service management

## Success Criteria

### Functional Requirements
- Archive 100% of messages from monitored rooms
- Preserve all media files with metadata
- Handle message edits and redactions
- Support encrypted rooms (if bot is member)
- Provide real-time and historical sync

### Performance Requirements
- Message archiving latency: <5 seconds
- Media download/upload: <30 seconds per file
- System resource usage: <500MB RAM, <10% CPU

### Reliability Requirements
- 99.9% uptime with automatic restart on failure
- Graceful handling of Matrix server downtime
- Comprehensive error logging

## Implementation Notes

This archiving system provides:
1. Simple backup for all Matrix communications
2. Long-term storage independent of Matrix server
3. Media preservation with Supabase CDN

The system integrates with our current Matrix server setup and can be deployed alongside the WhatsApp bridge.