#!/bin/bash
set -e

echo '╔══════════════════════════════════════╗'
echo '║     @AsTech — Product Container     ║'
echo '╚══════════════════════════════════════╝'

mkdir -p /var/log/as-tech /etc/hermes/data /etc/hermes/logs
export HERMES_HOME=/etc/hermes
export PATH="/usr/local/bin:/usr/bin:/bin:/opt/hermes-venv/bin"

if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo 'ERROR: DEEPSEEK_API_KEY is required!'
    exit 1
fi

# Write .env
printf "DEEPSEEK_API_KEY=%s\n" "$DEEPSEEK_API_KEY" > /etc/hermes/.env
printf "GATEWAY_ALLOW_ALL_USERS=true\n" >> /etc/hermes/.env

if [ ! -f /etc/hermes/profiles/as-tech/.initialized ]; then
    echo '[INIT] First run...'
    python3 /opt/hermes-source/init-hermes.py
    touch /etc/hermes/profiles/as-tech/.initialized
fi

cp /opt/hermes-source/generate-qr.js /tmp/generate-qr.js 2>/dev/null || true

echo '[START] Launching @AsTech Gateway...'
cd /opt/hermes-source
exec python3 -m hermes_cli.main gateway run --profile as-tech
