# Message Post-Processing - PRD 05

## Overview
This PRD outlines the implementation of intelligent message post-processing capabilities as messages are written to the database. The initial focus is on contextual message summarization, with an extensible architecture designed to support future media processing features like audio transcription and image analysis.

## Current State Analysis

### Database Integration Points
- Messages are written to `messages` table via archiver
- No current post-processing pipeline exists
- AI capabilities mentioned in CLAUDE.md but not implemented

### Existing Infrastructure
- PostgreSQL database with message storage
- Matrix archiver system capturing all room content
- Organizations system for content segmentation
- Extensible schema ready for additional post-processing types

## Core Feature: Contextual Message Summarization

**Trigger:** New message written to database
**Process:** 
- Retrieve last 100 messages from same room
- Generate contextual summary of new message
- Store summary with semantic importance score

**Use Cases:**
- Meeting recap generation
- Important decision tracking
- Context-aware search enhancement
- Daily/weekly room summaries

### 2. Database Schema Design
```sql
-- Core table for message summaries
CREATE TABLE message_summaries (
    id BIGSERIAL PRIMARY KEY,
    message_id BIGINT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    summary_text TEXT NOT NULL,
    context_importance_score FLOAT DEFAULT 0.0,
    processing_model VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(message_id)
);
```

### 3. Extensible Processing Queue System
**Future-Ready Design:** The processing system is designed to handle multiple content types as the platform grows.

```sql
-- Generic processing queue for all post-processing types
CREATE TABLE processing_queue (
    id BIGSERIAL PRIMARY KEY,
    item_type VARCHAR(20) NOT NULL, -- 'message', 'media' (for future)
    item_id BIGINT NOT NULL,
    processing_type VARCHAR(50) NOT NULL, -- 'summarization', 'transcription', 'image_analysis' (future)
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_processing_queue_status ON processing_queue(status, created_at);
```

## Technical Architecture

### 1. Processing Pipeline

#### 1.1 Message Processing Flow
```
Message Inserted → Database Trigger → Processing Queue → Background Worker → AI Summarization → Results Storage
```

#### 1.2 Extensible Design
The architecture supports future content types through a generic processing queue system:
```
Content Added → Type Detection → Queue Assignment → Appropriate Processor → Results Storage
```

#### 1.3 Queue System
**Technology:** PostgreSQL-based job queue (simple, reliable)
**Workers:** Background processes monitoring queue
**Retry Logic:** Exponential backoff for failed processing
**Rate Limiting:** Configurable processing limits to prevent resource overuse

### 2. AI Model Integration

#### 2.1 Summarization Models
**Local Models (Privacy-First):**
- Local LLM for summarization (Ollama/llama.cpp)
- Configurable model selection

**Cloud APIs (Enhanced Accuracy):**
- OpenAI GPT for summarization
- Anthropic Claude for complex analysis

#### 2.2 Model Configuration
```yaml
# config/ai.yaml
models:
  summarization:
    provider: "local"  # local, openai, anthropic
    model: "llama2-7b"
    max_context_length: 4096
  
  transcription:
    provider: "local"  # local, openai, google
    model: "whisper-medium"
    language: "auto"
  
  image_analysis:
    provider: "local"  # local, openai, google
    model: "clip-vit-base"
    enable_ocr: true
```

### 3. Database Integration

#### 3.1 Trigger-Based Processing
```sql
-- Trigger for new message processing
CREATE OR REPLACE FUNCTION trigger_message_processing()
RETURNS TRIGGER AS $$
BEGIN
    -- Queue message for post-processing
    INSERT INTO processing_queue (item_type, item_id, processing_type, created_at)
    VALUES ('message', NEW.id, 'summarization', NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER message_postprocess_trigger
    AFTER INSERT ON messages
    FOR EACH ROW EXECUTE FUNCTION trigger_message_processing();
```

#### 3.2 Processing Queue Table
```sql
CREATE TABLE processing_queue (
    id BIGSERIAL PRIMARY KEY,
    item_type VARCHAR(20) NOT NULL, -- 'message', 'media'
    item_id BIGINT NOT NULL,
    processing_type VARCHAR(50) NOT NULL, -- 'summarization', 'transcription', 'image_analysis'
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_processing_queue_status ON processing_queue(status, created_at);
```

## Implementation Plan

### Phase 1: Infrastructure Setup
- [ ] Set up processing queue system
- [ ] Create database schema for post-processing results
- [ ] Implement background worker framework
- [ ] Add configuration system for AI models

### Phase 2: Message Summarization
- [ ] Implement message context retrieval
- [ ] Integrate local LLM for summarization
- [ ] Create database triggers for new messages
- [ ] Add importance scoring algorithm
- [ ] Test with existing message data

### Phase 3: Video Transcription
- [ ] Implement audio extraction with FFmpeg
- [ ] Integrate Whisper for transcription
- [ ] Add language detection
- [ ] Create batch processing for existing videos
- [ ] Add transcription confidence scoring

### Phase 4: Image Analysis
- [ ] Implement object detection pipeline
- [ ] Add OCR capabilities for text extraction
- [ ] Create tagging system
- [ ] Add scene understanding
- [ ] Implement privacy-safe face detection

### Phase 5: Performance & Monitoring
- [ ] Add processing metrics and monitoring
- [ ] Implement rate limiting and throttling
- [ ] Add error handling and retry logic
- [ ] Create admin interface for processing status
- [ ] Performance optimization and caching

## Technical Specifications

### 1. Worker Service Architecture
```python
# services/postprocessor/worker.py
class PostProcessingWorker:
    def __init__(self, processing_type: str):
        self.processing_type = processing_type
        self.processors = {
            'summarization': MessageSummarizer(),
            'transcription': VideoTranscriber(),
            'image_analysis': ImageAnalyzer()
        }
    
    async def process_queue_item(self, item: QueueItem):
        processor = self.processors[item.processing_type]
        return await processor.process(item)
```

### 2. Configuration Management
**Environment Variables:**
- `AI_MODELS_PATH=/opt/ai-models` - Local model storage
- `PROCESSING_WORKERS=4` - Number of worker processes
- `MAX_QUEUE_SIZE=1000` - Queue size limit
- `ENABLE_LOCAL_MODELS=true` - Use local vs cloud models

### 3. Resource Management
**Processing Limits:**
- Max video size: 500MB
- Max image size: 50MB
- Max context messages: 100
- Processing timeout: 300 seconds per item

## Privacy and Security Considerations

### 1. Data Privacy
- All processing can be done locally to avoid cloud data exposure
- Option to disable processing for sensitive rooms
- Automatic PII detection and redaction in summaries
- Configurable data retention for processing results

### 2. Resource Security
- Processing worker isolation
- File type validation and sanitization
- Memory and CPU usage limits
- Malware scanning for uploaded media

### 3. Access Control
- Organization-based processing permissions
- Room-level processing configuration
- User opt-out capabilities
- Admin controls for processing features

## Success Metrics

### 1. Processing Performance
- 95% of messages processed within 30 seconds
- 90% of videos transcribed within 5 minutes
- 99% processing success rate
- <2 second query response for processed content

### 2. Quality Metrics
- Summary relevance score >4/5 (user feedback)
- Transcription accuracy >95% (WER metric)
- Image tag accuracy >90% (precision/recall)
- Zero false positive content flags

### 3. System Health
- Processing worker uptime >99.5%
- Queue processing lag <1 minute average
- Database performance impact <10%
- Storage efficiency >80% (compressed results)

## Benefits

### 1. Enhanced Search and Discovery
- Semantic search across summarized content
- Visual content discovery via image tags
- Audio content searchability via transcriptions
- Context-aware content recommendations

### 2. Productivity Improvements
- Automated meeting summaries
- Important message highlighting
- Visual content cataloging
- Audio content accessibility

### 3. Compliance and Archival
- Searchable archive creation
- Content classification automation
- Automated content moderation
- Long-term data value enhancement

## Migration Strategy

### 1. Backward Compatibility
- All existing data remains unchanged
- Post-processing is additive functionality
- Gradual rollout with feature flags
- Fallback modes for processing failures

### 2. Existing Data Processing
- Batch processing script for historical messages
- Prioritized processing for recent content
- Rate-limited processing to avoid system impact
- Progress tracking and resumable processing

## Next Steps

1. Review and approve PRD
2. Set up development environment with AI models
3. Implement Phase 1 infrastructure
4. Create processing pipeline prototypes
5. Test with sample data and measure performance
6. Gradual rollout with monitoring and feedback collection

## Appendix: Example Queries

**Message Summaries:**
```sql
-- Find important messages in a room
SELECT m.content, ms.summary_text, ms.context_importance_score
FROM messages m
JOIN message_summaries ms ON m.id = ms.message_id
WHERE m.room_name = 'Engineering Team'
AND ms.context_importance_score > 0.8
ORDER BY ms.context_importance_score DESC;
```

**Media Search:**
```sql
-- Find images containing specific objects
SELECT m.file_path, ma.tags, ma.summary_text
FROM media m
JOIN media_analysis ma ON m.id = ma.media_id
WHERE 'whiteboard' = ANY(ma.tags)
AND ma.analysis_type = 'object_detection';

-- Search transcribed video content
SELECT m.file_path, mt.transcription_text, mt.summary_text
FROM media m
JOIN media_transcriptions mt ON m.id = mt.media_id
WHERE mt.transcription_text ILIKE '%quarterly results%';
```