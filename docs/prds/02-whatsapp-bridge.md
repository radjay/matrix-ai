# PRD: WhatsApp Bridge for Matrix Server

## Overview
Implement a WhatsApp bridge to allow Matrix users to communicate bidirectionally with WhatsApp contacts and groups through our existing Matrix server at matrix.radx.dev.

## Objectives
- Enable Matrix users to send/receive WhatsApp messages without leaving Matrix
- Bridge WhatsApp groups as Matrix rooms
- Maintain message history and media sharing capabilities
- Integrate seamlessly with existing Element Web interface

## User Stories

### Primary Users: Matrix Server Users
- **As a Matrix user**, I want to connect my WhatsApp account so I can receive WhatsApp messages in Matrix
- **As a Matrix user**, I want to send messages to WhatsApp contacts from my Matrix client
- **As a Matrix user**, I want WhatsApp groups to appear as Matrix rooms
- **As a Matrix user**, I want to share media (images, documents, voice messages) between WhatsApp and Matrix
- **As a Matrix user**, I want my WhatsApp chat history to be available in Matrix

## Technical Requirements

### Core Functionality
- **Bidirectional messaging**: Messages flow both ways between WhatsApp and Matrix
- **Media support**: Images, videos, documents, voice messages, stickers
- **Group chat bridging**: WhatsApp groups become Matrix rooms
- **Contact management**: WhatsApp contacts appear as Matrix users
- **Message history**: Sync existing WhatsApp conversations to Matrix
- **Real-time sync**: Messages appear in both platforms simultaneously

### Authentication & Setup
- **WhatsApp Web authentication**: QR code scanning for initial setup
- **Persistent sessions**: Maintain WhatsApp connection across restarts
- **User onboarding**: Simple setup flow through Matrix bot commands

### Integration Requirements
- **PostgreSQL integration**: Use existing database for bridge data
- **Matrix Appservice**: Register as official Matrix application service
- **Element Web compatibility**: Bridge users appear correctly in Element interface
- **Existing user accounts**: Work with current Matrix user accounts

## Technical Architecture

### Components
1. **mautrix-whatsapp bridge** (Go binary)
   - WhatsApp Web protocol client
   - Matrix Appservice implementation
   - Message translation and routing

2. **PostgreSQL database** (existing)
   - Bridge state and configuration
   - User session management
   - Message mapping and history

3. **Matrix Synapse** (existing)
   - Appservice registration
   - Bridge user management
   - Room and message handling

### System Integration
```
WhatsApp Mobile App → WhatsApp Web Protocol → mautrix-whatsapp bridge → Matrix Synapse → Element Web
                                                        ↓
                                                 PostgreSQL Database
```

### File Structure
```
/home/matrix-ai/
├── config/
│   ├── matrix-synapse/
│   │   ├── homeserver.yaml (updated with bridge registration)
│   │   └── whatsapp-registration.yaml (new)
│   └── mautrix-whatsapp/
│       ├── config.yaml
│       └── registration.yaml
├── logs/
│   └── mautrix-whatsapp.log
└── data/
    └── mautrix-whatsapp/ (session data)
```

## Implementation Phases

### Phase 1: Bridge Installation & Configuration
- Download pre-compiled mautrix-whatsapp binary from GitHub releases
- Configure PostgreSQL database tables
- Generate Matrix appservice registration
- Create systemd service for bridge
- Update Synapse configuration

### Phase 2: User Onboarding & Authentication
- Set up bridge bot (@whatsappbot:matrix.radx.dev)
- Implement QR code authentication flow
- Test basic message bridging
- Verify media file transfers
- Test group chat bridging

### Phase 3: Advanced Features & Optimization
- Enable message history sync
- Implement double puppeting (optional)
- Add bridge management commands
- Performance optimization
- Monitoring and logging setup

## User Experience Flow

### Initial Setup
1. User sends message to @whatsappbot:matrix.radx.dev
2. Bot responds with setup instructions
3. User types `login` command
4. Bot provides QR code or login link
5. User scans QR code with WhatsApp mobile app
6. Bridge establishes connection and begins syncing

### Daily Usage
1. WhatsApp messages appear automatically in Matrix as direct messages
2. WhatsApp groups appear as Matrix rooms
3. User can reply to WhatsApp messages through Matrix interface
4. Media files are automatically transferred and displayed
5. New WhatsApp contacts automatically create Matrix rooms

## Technical Specifications

### Database Requirements
- Extend existing PostgreSQL database with bridge tables
- Store user sessions, room mappings, and message state
- Backup strategy includes bridge data

### Network Requirements
- Outbound HTTPS to WhatsApp servers (web.whatsapp.com)
- Bridge listens on localhost port (e.g., 29318)
- Communication with Matrix Synapse via existing HTTP endpoint

### Performance Requirements
- Support 50+ concurrent WhatsApp users
- Message latency < 5 seconds under normal conditions
- Handle media files up to 100MB (WhatsApp limit)
- Maintain 24/7 uptime with auto-restart on failure

### Security Requirements
- Bridge runs as non-root user
- Configuration files protected with appropriate permissions
- Session data encrypted at rest
- Rate limiting to prevent abuse

## Success Criteria

### Functional Success
- Users can successfully link WhatsApp accounts
- Bidirectional messaging works reliably
- Group chats are properly bridged
- Media files transfer correctly
- Message history is accessible

### Technical Success
- Bridge service runs reliably with >99% uptime
- Integration with existing Matrix server is seamless
- Performance meets specified requirements
- Setup process is documented and reproducible

### User Success
- Setup process takes < 10 minutes for typical user
- Bridge functionality is intuitive within Element Web
- Users can manage bridge settings through Matrix commands

## Out of Scope

### Excluded Features
- Voice/video call bridging (not supported by mautrix-whatsapp)
- WhatsApp Business API integration
- Multi-device WhatsApp support beyond WhatsApp Web
- Custom WhatsApp client development

### Future Considerations
- Instagram/Facebook Messenger bridges (similar architecture)
- Signal bridge integration
- Advanced bridge management web interface
- Enterprise features and user management

## Dependencies

### External Dependencies
- WhatsApp Web protocol stability
- WhatsApp account requires mobile app presence every ~2 weeks
- Internet connectivity for WhatsApp servers

### Internal Dependencies
- Existing PostgreSQL database
- Matrix Synapse configuration access
- systemd service management
- nginx reverse proxy (existing)

## Risks & Mitigations

### Technical Risks
- **WhatsApp protocol changes**: Monitor mautrix-whatsapp updates
- **Account suspension**: Follow WhatsApp ToS, avoid automation abuse
- **Bridge crashes**: Implement auto-restart and monitoring
- **Database issues**: Regular backups and monitoring

### Operational Risks
- **User support**: Document common issues and solutions
- **Performance degradation**: Monitor resource usage and optimize
- **Security vulnerabilities**: Keep bridge software updated

## Maintenance Requirements

### Regular Tasks
- Monitor bridge service health
- Update mautrix-whatsapp when new versions are released
- Backup bridge database tables
- Monitor WhatsApp connection status for users

### User Support
- Provide documentation for common bridge issues
- Help users reconnect when WhatsApp sessions expire
- Troubleshoot message delivery problems

## Success Metrics

### Technical Metrics
- Bridge uptime percentage
- Message delivery success rate
- Average message latency
- Number of active bridge users

### User Metrics
- Bridge adoption rate among Matrix users
- User retention after initial setup
- Support ticket volume related to bridge

---

*This PRD defines the implementation of a WhatsApp bridge for our Matrix server using direct installation methods consistent with our existing infrastructure.*