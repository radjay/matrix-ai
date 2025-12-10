# Matrix AI Server - Development Rules

## Project Context
AI-enabled Matrix server with message summarization, chat with message history, content analysis, and enhanced user interactions.

## Repository Structure

```
/home/matrix-ai/
├── services/                    # All services live here
│   ├── archiver/               # Message archiver (Python)
│   │   ├── bin/                # Main executables
│   │   ├── config/             # Service configuration
│   │   ├── data/               # Migrations, backups
│   │   └── scripts/            # Helper scripts
│   │
│   ├── whatsapp-bridge/        # WhatsApp bridge (Go)
│   │   ├── bin/                # mautrix-whatsapp binary
│   │   └── config/             # Bridge configuration
│   │
│   ├── matrix-synapse/         # Matrix server config
│   │   └── config/             # Synapse configuration
│   │
│   └── ai/                     # Future AI services
│       └── models/             # AI model storage
│
├── scripts/                    # Global orchestration scripts
│   ├── start-matrix.sh
│   ├── stop-matrix.sh
│   ├── status-matrix.sh
│   └── setup.sh
│
├── logs/                       # Service logs (gitignored)
│
├── data/                       # Runtime data (gitignored)
│   └── media_store/            # Matrix media files
│
├── docs/                       # Documentation
│   └── prds/                   # Product requirement docs
│
└── tests/                      # Test files
    └── tmp/                    # Temporary test scripts
```

## Development Commands

### Service Management
```bash
npm start          # Start all services
npm stop           # Stop all services
npm restart        # Restart all services
npm run status     # Check service status
npm run versions   # Show installed versions
```

### Viewing Logs
```bash
npm run logs           # Archiver logs (default)
npm run logs:bridge    # WhatsApp bridge logs
npm run logs:synapse   # Matrix Synapse logs
npm run logs:archiver  # Archiver logs
```

### Direct Script Access
```bash
./scripts/start-matrix.sh
./scripts/stop-matrix.sh
./scripts/status-matrix.sh
```

## Development Rules

### Code Standards
- Follow existing code patterns and conventions
- Python for archiver/AI services, shell scripts for orchestration
- Write tests for new functionality
- Document AI model requirements and configurations

### Security Requirements
- Never commit secrets or API keys to repository
- Config files with secrets are gitignored (only .example files tracked)
- Use environment variables for sensitive configuration
- Validate all user inputs, especially for AI processing

### Adding New Services
1. Create directory under `services/<service-name>/`
2. Include: `bin/`, `config/`, `scripts/` subdirectories
3. Add `.example` config files (actual configs are gitignored)
4. Update `scripts/start-matrix.sh` if service should auto-start
5. Document in this file

### Testing Standards
- Write unit tests for core functionality
- Integration tests for AI components
- Create temporary test scripts in `/tests/tmp/` folder
- Clean up test scripts when no longer needed
