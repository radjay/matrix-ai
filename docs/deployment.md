# Matrix Server with WhatsApp Bridge - Deployment Guide

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
sudo nano setup.sh
# Update these lines:
# DOMAIN="your-domain.com"
# EMAIL="your-email@domain.com"
```

#### 3. Run Automated Setup
```bash
sudo bash setup.sh
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
/opt/matrix/synapse-venv/bin/register_new_matrix_user -c config/matrix-synapse/homeserver.yaml https://your-domain.com
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

## Manual Installation Steps

If you prefer to install components individually:

### Phase 1: Matrix Server Setup

1. **System Dependencies**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx certbot python3-certbot-nginx ufw fail2ban
```

2. **PostgreSQL Setup**
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo -u postgres createuser matrix
sudo -u postgres createdb matrix --owner=matrix
sudo -u postgres psql -c "ALTER USER matrix PASSWORD 'your-secure-password';"
```

3. **Matrix Synapse Installation**
```bash
sudo mkdir -p /opt/matrix
sudo python3 -m venv /opt/matrix/synapse-venv
sudo /opt/matrix/synapse-venv/bin/pip install matrix-synapse[postgres]
```

4. **Configuration and SSL**
- Generate Synapse config
- Configure nginx reverse proxy  
- Obtain Let's Encrypt certificates
- Start Matrix services

### Phase 2: Element Web Client

1. **Download and Configure**
```bash
cd /var/www
sudo wget https://github.com/element-hq/element-web/releases/latest/download/element-*.tar.gz
sudo tar -xzf element-*.tar.gz
sudo mv element-* element
sudo cp element/config.sample.json element/config.json
# Edit config.json to point to your domain
```

2. **Update nginx Configuration**
- Add Element Web serving location
- Maintain Matrix API proxy endpoints

### Phase 3: WhatsApp Bridge

1. **Download Bridge Binary**
```bash
wget https://github.com/mautrix/whatsapp/releases/latest/download/mautrix-whatsapp-amd64
chmod +x mautrix-whatsapp-amd64
```

2. **Configure Bridge**
```bash
./mautrix-whatsapp-amd64 --generate-example-config > config.yaml
# Edit config.yaml with database and homeserver details
```

3. **Register with Matrix**
```bash
./mautrix-whatsapp-amd64 -g -c config.yaml -r registration.yaml
# Add registration.yaml to Synapse app_service_config_files
```

4. **Start Bridge Service**
```bash
# Create systemd service
# Start and enable bridge
```

## Troubleshooting

### Common Issues

**Matrix Synapse won't start:**
```bash
sudo journalctl -xeu matrix-synapse
# Check database connection and config file permissions
```

**WhatsApp bridge not responding:**
```bash
sudo journalctl -xeu mautrix-whatsapp
# Verify database config and Matrix appservice registration
```

**SSL certificate issues:**
```bash
sudo certbot certificates
sudo certbot renew --dry-run
```

**nginx configuration errors:**
```bash
sudo nginx -t
# Check proxy settings and SSL certificate paths
```

### Service Management

```bash
# Check all services
sudo systemctl status matrix-synapse mautrix-whatsapp nginx postgresql

# Restart services
sudo systemctl restart matrix-synapse
sudo systemctl restart mautrix-whatsapp

# View logs
sudo journalctl -f -u matrix-synapse
sudo journalctl -f -u mautrix-whatsapp
```

### File Locations

- **Matrix Config**: `/home/matrix-ai/config/matrix-synapse/`
- **Bridge Config**: `/home/matrix-ai/config/mautrix-whatsapp/`
- **Element Web**: `/var/www/element/`
- **nginx Config**: `/etc/nginx/sites-available/your-domain.com`
- **Logs**: `/home/matrix-ai/logs/`
- **SSL Certificates**: `/etc/letsencrypt/live/your-domain.com/`

## Security Considerations

- **Firewall**: Only ports 22 (SSH) and 443 (HTTPS) are open
- **Database**: PostgreSQL with secure password (stored in .env)
- **SSL**: Strong ciphers and HSTS enabled
- **Bridge**: Runs as non-root user with restricted permissions
- **Updates**: Regular security updates recommended

## Performance Tuning

### For High-Traffic Servers

1. **PostgreSQL Optimization**
```bash
# Edit /etc/postgresql/*/main/postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
max_connections = 200
```

2. **nginx Optimization**
```bash
# Edit /etc/nginx/nginx.conf
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
```

3. **Matrix Synapse Tuning**
```bash
# Edit homeserver.yaml
database:
  args:
    cp_min: 10
    cp_max: 50
```

## Architecture Overview

```
Internet → nginx (SSL termination) → Matrix Synapse (port 8008)
                ↓                           ↓
         Element Web Client          PostgreSQL Database
                                            ↓
                                    WhatsApp Bridge
                                            ↓
                                     WhatsApp Web API
```

### Components

- **nginx**: Reverse proxy handling SSL and serving Element Web
- **Matrix Synapse**: Core Matrix homeserver handling federation and client API
- **PostgreSQL**: Database storing Matrix rooms, messages, and user data
- **Element Web**: Browser-based Matrix client
- **mautrix-whatsapp**: Bridge service connecting WhatsApp to Matrix
- **systemd**: Service management for all components

### Network Flow

1. **Web Clients** → nginx → Element Web static files
2. **Matrix API** → nginx → Matrix Synapse → PostgreSQL  
3. **Bridge Messages** → WhatsApp API → mautrix-whatsapp → Matrix Synapse
4. **SSL/TLS**: Handled by nginx with Let's Encrypt certificates

This setup provides a complete, production-ready Matrix server with WhatsApp integration.