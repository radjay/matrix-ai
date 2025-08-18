#!/bin/bash
# Restart all Matrix services

set -e

echo "🔄 Restarting Matrix AI Server Services..."
echo

# Stop all services first
echo "Stopping services..."
/home/matrix-ai/scripts/stop-matrix.sh

echo
echo "Waiting for clean shutdown..."
sleep 3

echo "Starting services..."
/home/matrix-ai/scripts/start-matrix.sh

echo "🎉 Matrix AI Server restart complete!"