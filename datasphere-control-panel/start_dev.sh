#!/bin/bash
echo "🚀 Starting Ailien Platform Control Panel - DEV Environment"
echo ""
cd "$(dirname "$0")"
python dev_server.py --env dev