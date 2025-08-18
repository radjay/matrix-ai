#!/bin/bash

# WhatsApp Bridge Health Monitor
# This script checks the bridge health and logs status

LOG_FILE="/home/matrix-ai/logs/bridge-monitor.log"
BRIDGE_LOG="/home/matrix-ai/logs/mautrix-whatsapp.log"
BRIDGE_ERROR_LOG="/home/matrix-ai/logs/mautrix-whatsapp-errors.log"

# Function to log with timestamp
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check if bridge process is running
check_bridge_process() {
    if pgrep -f "mautrix-whatsapp" > /dev/null; then
        log_message "INFO: Bridge process is running"
        return 0
    else
        log_message "ERROR: Bridge process is not running"
        return 1
    fi
}

# Check if bridge is responding on HTTP port
check_bridge_http() {
    if curl -s "http://localhost:29318" > /dev/null 2>&1; then
        log_message "INFO: Bridge HTTP endpoint is responding"
        return 0
    else
        log_message "ERROR: Bridge HTTP endpoint is not responding"
        return 1
    fi
}

# Check recent errors in logs
check_recent_errors() {
    if [ -f "$BRIDGE_ERROR_LOG" ]; then
        ERROR_COUNT=$(tail -100 "$BRIDGE_ERROR_LOG" 2>/dev/null | grep -c "ERROR\|FATAL" 2>/dev/null || echo "0")
        if [ "$ERROR_COUNT" -gt 0 ] 2>/dev/null; then
            log_message "WARN: Found $ERROR_COUNT recent errors in bridge logs"
            return 1
        else
            log_message "INFO: No recent errors in bridge logs"
            return 0
        fi
    else
        log_message "INFO: No error log file found"
        return 0
    fi
}

# Check database connectivity
check_database() {
    if sudo -u postgres psql -d matrix -c "SELECT 1;" > /dev/null 2>&1; then
        log_message "INFO: Database connection is healthy"
        return 0
    else
        log_message "ERROR: Database connection failed"
        return 1
    fi
}

# Main monitoring function
main() {
    log_message "Starting bridge health check"
    
    HEALTH_SCORE=0
    
    if check_bridge_process; then
        ((HEALTH_SCORE++))
    fi
    
    if check_bridge_http; then
        ((HEALTH_SCORE++))
    fi
    
    if check_recent_errors; then
        ((HEALTH_SCORE++))
    fi
    
    if check_database; then
        ((HEALTH_SCORE++))
    fi
    
    log_message "Health check completed - Score: $HEALTH_SCORE/4"
    
    if [ "$HEALTH_SCORE" -eq 4 ]; then
        log_message "STATUS: Bridge is healthy"
        exit 0
    elif [ "$HEALTH_SCORE" -ge 2 ]; then
        log_message "STATUS: Bridge has minor issues"
        exit 1
    else
        log_message "STATUS: Bridge has major issues"
        exit 2
    fi
}

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Run main function
main