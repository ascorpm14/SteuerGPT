#!/bin/bash
# @AsTech — Quick Start Script
# Usage: bash quick-start.sh

echo "╔══════════════════════════════════════╗"
echo "║     @AsTech — Quick Start           ║"
echo "║     Prêt à lancer !                  ║"
echo "╚══════════════════════════════════════╝"

# 1. Start n8n
echo "[1/4] Démarrage n8n..."
docker run -d --name as-tech-n8n --restart unless-stopped -p 5678:5678 \
  -v as-tech-n8n-data:/home/node/.n8n \
  -e N8N_PORT=5678 -e N8N_HOST=0.0.0.0 \
  n8nio/n8n:latest 2>/dev/null && echo "  ✅ n8n OK" || echo "  ⚠️ n8n déjà lancé"

# 2. Start @AsTech Hermes
echo "[2/4] Démarrage @AsTech..."
docker run -d --name as-tech-hermes --restart unless-stopped \
  --link as-tech-n8n \
  -v as-tech-memories:/etc/hermes/profiles/as-tech/memories \
  -v /root/steuergpt/hermes/profiles/as-tech/data:/etc/hermes/profiles/as-tech/data \
  -v /root/steuergpt/hermes/profiles/as-tech/skills:/etc/hermes/profiles/as-tech/skills:ro \
  -e DEEPSEEK_API_KEY="${DEEP...n\
  as-tech-hermes:final 2>/dev/null && echo \"  ✅ @AsTech OK\" || echo \"  ⚠️ @AsTech déjà lancé\"

sleep 3

# 3. Status
echo \"[3/4] Vérification...\"
docker ps --format 'table {{.ID}}\\t{{.Image}}\\t{{.Status}}\\t{{.Names}}'

# 4. Instructions WhatsApp
echo \"\"
echo \"[4/4] Pour connecter WhatsApp :\"
echo \"  docker exec -e NODE_PATH=/usr/lib/node_modules as-tech-hermes node /opt/hermes-source/generate-qr.js\"
echo \"\" 
echo \"✅ @AsTech est prêt !\"
