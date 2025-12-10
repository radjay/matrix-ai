# Matrix Server with WhatsApp Bridge - Deployment Guide

## Component Versions

This repository is tested with the following versions:

| Component | Version | Release Date |
|-----------|---------|--------------|
| **Matrix Synapse** | 1.143.0 | November 2025 |
| **Element Web** | 1.12.1 | December 2025 |
| **mautrix-whatsapp** | 0.12.4 | August 2025 |

> **Note**: Check for newer versions before deploying:
> - [Synapse Releases](https://github.com/element-hq/synapse/releases)
> - [Element Web Releases](https://github.com/element-hq/element-web/releases)
> - [mautrix-whatsapp Releases](https://github.com/mautrix/whatsapp/releases)

## Quick Setup (Fresh VPS)

Complete automated setup for Matrix server with WhatsApp bridge integration.

### What Gets Installed

- **Matrix Synapse** - Matrix homeserver with PostgreSQL database
- **Element Web** - Web client interface accessible via browser
- **WhatsApp Bridge** - Bidirectional messaging between WhatsApp and Matrix
- **nginx** - Reverse proxy with SSL/TLS termination
- **Let's Encrypt** - Automatic SSL certificate management

### Prerequisites

1. **Fresh Ubuntu VPS** (22.04 or 24.04) with root access
2. **Domain name** pointing to your VPS IP address
3. **SSH access** configured with key authentication
4. **Email address** for SSL certificate registration

### Deployment Steps

#### 1. Clone the Repository
```bash
git clone <repository-url> /home/matrix-ai
cd /home/matrix-ai
```

#### 2. Configure Environment
```bash
# Generate secure database password
echo "MATRIX_DB_PASSWORD=$(openssl rand -base64 32)" > .env

# Edit setup.sh to set your domain and email
sudo nano scripts/setup.sh
# Update these lines:
# DOMAIN="your-domain.com"
# EMAIL="your-email@domain.com"
```

#### 3. Run Automated Setup
```bash
sudo bash scripts/setup.sh
```

The script will automatically:
- Install all system dependencies
- Configure PostgreSQL database
- Install Matrix Synapse in virtual environment
- Set up nginx with SSL certificates
- Deploy Element Web client
- Install and configure WhatsApp bridge
- Start all services

### Post-Installation Setup

After the script completes successfully:

#### 1. Create Admin User
```bash
cd /home/matrix-ai
/opt/matrix/synapse-venv/bin/register_new_matrix_user \
  -c services/matrix-synapse/config/homeserver.yaml \
  https://your-domain.com
```

#### 2. Test Matrix Server
- Visit `https://your-domain.com` - Element Web should load
- Create account or login with admin user
- Test sending messages

#### 3. Connect WhatsApp Bridge
- In Element Web, start chat with `@whatsappbot:your-domain.com`
- Type `login` to get QR code
- Scan QR code with WhatsApp mobile app
- Your WhatsApp chats will sync to Matrix

#### 4. Configure SSL Auto-Renewal
```bash
sudo crontab -e
# Add this line:
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## Manual Installation Steps

If you prefer to install components individually or need to update specific components.

### Phase 1: System Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
  python3 python3-pip python3-venv \
  postgresql postgresql-contrib \
  nginx certbot python3-certbot-nginx \
  ufw fail2ban wget curl
```

### Phase 2: PostgreSQL Setup

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo -u postgres createuser matrix
sudo -u postgres createdb matrix --owner=matrix
sudo -u postgres psql -c "ALTER USER matrix PASSWORD 'your-secure-password';"
```

### Phase 3: Matrix Synapse Installation

```bash
# Create virtual environment
sudo mkdir -p /opt/matrix
sudo python3 -m venv /opt/matrix/synapse-venv

# Install Synapse (specific version)
sudo /opt/matrix/synapse-venv/bin/pip install 'matrix-synapse[postgres]==1.143.0'

# Or install latest
sudo /opt/matrix/synapse-venv/bin/pip install 'matrix-synapse[postgres]'
```

**Configuration:**
- Copy example config: `cp services/matrix-synapse/config/homeserver.example.yaml services/matrix-synapse/config/homeserver.yaml`
- Edit with your domain and database credentials
- Generate signing key if needed

**Systemd Service:**
```bash
# Link service file
sudo ln -sf /home/matrix-ai/services/matrix-synapse/matrix-synapse.service \
  /etc/systemd/system/matrix-synapse.service
sudo systemctl daemon-reload
sudo systemctl enable matrix-synapse
```

### Phase 4: Element Web Installation

```bash
# Set version
ELEMENT_VERSION="1.12.1"

# Download and extract
cd /var/www
sudo wget "https://github.com/element-hq/element-web/releases/download/v${ELEMENT_VERSION}/element-v${ELEMENT_VERSION}.tar.gz"
sudo tar -xzf "element-v${ELEMENT_VERSION}.tar.gz"
sudo mv "element-v${ELEMENT_VERSION}" element
sudo rm "element-v${ELEMENT_VERSION}.tar.gz"

# Configure
sudo cp element/config.sample.json element/config.json
sudo nano element/config.json
# Set "default_server_config.m.homeserver.base_url" to your domain
```

**Updating Element Web:**
```bash
ELEMENT_VERSION="1.12.1"  # Change to new version
cd /var/www
sudo wget "https://github.com/element-hq/element-web/releases/download/v${ELEMENT_VERSION}/element-v${ELEMENT_VERSION}.tar.gz"
sudo tar -xzf "element-v${ELEMENT_VERSION}.tar.gz"
sudo mv element element.old
sudo mv "element-v${ELEMENT_VERSION}" element
sudo cp element.old/config.json element/config.json
sudo rm "element-v${ELEMENT_VERSION}.tar.gz"
# Test, then: sudo rm -rf element.old
```

### Phase 5: WhatsApp Bridge Installation

```bash
# Set version
WHATSAPP_VERSION="0.12.4"

# Download binary
cd /home/matrix-ai/services/whatsapp-bridge/bin
sudo wget "https://github.com/mautrix/whatsapp/releases/download/v${WHATSAPP_VERSION}/mautrix-whatsapp-amd64" \
  -O mautrix-whatsapp
sudo chmod +x mautrix-whatsapp

# Verify
./mautrix-whatsapp --version
```

**Configuration:**
```bash
# Generate example config (if starting fresh)
cd /home/matrix-ai/services/whatsapp-bridge
./bin/mautrix-whatsapp --generate-example-config > config/config.yaml

# Edit configuration
nano config/config.yaml
# Set homeserver URL, database, and permissions

# Generate registration file
./bin/mautrix-whatsapp -g -c config/config.yaml -r config/registration.yaml

# Add to Synapse config (homeserver.yaml):
# app_service_config_files:
#   - /home/matrix-ai/services/whatsapp-bridge/config/registration.yaml
```

**Updating WhatsApp Bridge:**
```bash
WHATSAPP_VERSION="0.12.4"  # Change to new version
cd /home/matrix-ai/services/whatsapp-bridge/bin

# Stop bridge first
pkill -f mautrix-whatsapp

# Download new version
sudo wget "https://github.com/mautrix/whatsapp/releases/download/v${WHATSAPP_VERSION}/mautrix-whatsapp-amd64" \
  -O mautrix-whatsapp.new
sudo chmod +x mautrix-whatsapp.new
sudo mv mautrix-whatsapp mautrix-whatsapp.old
sudo mv mautrix-whatsapp.new mautrix-whatsapp

# Restart services
cd /home/matrix-ai
./scripts/start-matrix.sh
```

---

## Updating All Components

Use these commands to update to the latest versions:

```bash
cd /home/matrix-ai

# Stop all services
./scripts/stop-matrix.sh

# Update Matrix Synapse
sudo /opt/matrix/synapse-venv/bin/pip install --upgrade matrix-synapse

# Update Element Web (replace version as needed)
ELEMENT_VERSION="1.12.1"
cd /var/www
sudo wget "https://github.com/element-hq/element-web/releases/download/v${ELEMENT_VERSION}/element-v${ELEMENT_VERSION}.tar.gz"
sudo tar -xzf "element-v${ELEMENT_VERSION}.tar.gz"
sudo mv element element.old && sudo mv "element-v${ELEMENT_VERSION}" element
sudo cp element.old/config.json element/config.json
sudo rm "element-v${ELEMENT_VERSION}.tar.gz"

# Update WhatsApp Bridge (replace version as needed)
WHATSAPP_VERSION="0.12.4"
cd /home/matrix-ai/services/whatsapp-bridge/bin
sudo wget "https://github.com/mautrix/whatsapp/releases/download/v${WHATSAPP_VERSION}/mautrix-whatsapp-amd64" -O mautrix-whatsapp.new
sudo chmod +x mautrix-whatsapp.new
sudo mv mautrix-whatsapp mautrix-whatsapp.old && sudo mv mautrix-whatsapp.new mautrix-whatsapp

# Start all services
cd /home/matrix-ai
./scripts/start-matrix.sh

# Verify versions
echo "Synapse: $(/opt/matrix/synapse-venv/bin/python -c 'import synapse; print(synapse.__version__)')"
echo "Element: $(cat /var/www/element/version)"
echo "WhatsApp: $(./services/whatsapp-bridge/bin/mautrix-whatsapp --version)"
```

---

## Service Management

```bash
# Start all services
./scripts/start-matrix.sh

# Stop all services
./scripts/stop-matrix.sh

# Check status
./scripts/status-matrix.sh

# View logs
tail -f logs/archiver.log
tail -f logs/bridge.log
sudo journalctl -f -u matrix-synapse
```

---

## File Locations

| Component | Location |
|-----------|----------|
| **Synapse Config** | `/home/matrix-ai/services/matrix-synapse/config/` |
| **Synapse Binary** | `/opt/matrix/synapse-venv/` |
| **WhatsApp Bridge** | `/home/matrix-ai/services/whatsapp-bridge/` |
| **Archiver** | `/home/matrix-ai/services/archiver/` |
| **Element Web** | `/var/www/element/` |
| **nginx Config** | `/etc/nginx/sites-available/your-domain` |
| **Logs** | `/home/matrix-ai/logs/` |
| **Media Store** | `/home/matrix-ai/data/media_store/` |
| **SSL Certificates** | `/etc/letsencrypt/live/your-domain/` |

---

## Troubleshooting

### Matrix Synapse won't start
```bash
sudo journalctl -xeu matrix-synapse
# Check database connection and config file permissions
```

### WhatsApp bridge not responding
```bash
tail -f /home/matrix-ai/logs/mautrix-whatsapp.log
# Verify database config and Matrix appservice registration
```

### SSL certificate issues
```bash
sudo certbot certificates
sudo certbot renew --dry-run
```

### Check all service versions
```bash
echo "=== Installed Versions ==="
echo "Synapse: $(/opt/matrix/synapse-venv/bin/python -c 'import synapse; print(synapse.__version__)')"
echo "Element: $(cat /var/www/element/version)"
echo "WhatsApp: $(/home/matrix-ai/services/whatsapp-bridge/bin/mautrix-whatsapp --version 2>&1 | head -1)"
```

---

## Architecture

```
Internet → nginx (SSL) → Matrix Synapse → PostgreSQL
             ↓                ↓
      Element Web Client  WhatsApp Bridge → WhatsApp Web API
                               ↓
                          Archiver → Supabase
```

### Repository Structure

```
/home/matrix-ai/
├── services/
│   ├── matrix-synapse/    # Synapse configuration
│   ├── whatsapp-bridge/   # Bridge binary + config
│   ├── archiver/          # Message archiver
│   └── ai/                # Future AI services
├── scripts/               # Service management
├── logs/                  # Service logs
├── data/                  # Runtime data (media)
└── docs/                  # Documentation
```
