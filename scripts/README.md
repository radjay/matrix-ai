# Matrix AI Server Management Scripts

Convenient scripts to manage all Matrix services like an npm start/stop.

## Available Scripts

### 🚀 Start Services
```bash
./scripts/start-matrix.sh
```
Starts all services in correct dependency order:
1. Synapse Matrix Server
2. WhatsApp Bridge  
3. Matrix Archiver

### 🛑 Stop Services
```bash
./scripts/stop-matrix.sh
```
Stops all services in reverse dependency order.

### 🔄 Restart Services
```bash
./scripts/restart-matrix.sh
```
Cleanly stops and restarts all services.

### 📊 Check Status
```bash
./scripts/status-matrix.sh
```
Shows current status of all services with PIDs, memory usage, and useful links.

### 🔍 Monitor Bridge
```bash
./scripts/monitor-bridge.sh
```
Monitors WhatsApp bridge connectivity and status.

## Service Dependencies

```
PostgreSQL (always running)
    ↓
Synapse Matrix Server
    ↓  
WhatsApp Bridge
    ↓
Matrix Archiver
```

## Log Files

- **Synapse**: `journalctl -u matrix-synapse -f`
- **Bridge**: `tail -f /home/matrix-ai/logs/bridge.log`
- **Archiver**: `tail -f /home/matrix-ai/logs/archiver.log`
- **Bridge JSON**: `tail -f /home/matrix-ai/logs/mautrix-whatsapp.log`

## Service URLs

- **Element Web**: http://localhost:8080
- **Synapse API**: http://localhost:8008
- **WhatsApp Bridge**: http://localhost:29318