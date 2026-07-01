#!/bin/bash
# @AsTech — System Status
echo "═══════════════════════════════════════"
echo "  @AsTech — System Status"
echo "═══════════════════════════════════════"
echo ""
echo "📦 Containers:"
docker ps --format 'table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}' 2>/dev/null || echo "  (docker not available)"
echo ""
echo "👥 Clients:"
DATA_DIR="/root/steuergpt/hermes/profiles/as-tech/data"
if [ -d "$DATA_DIR" ]; then
    count=0
    for d in "$DATA_DIR"/client_*/; do
        if [ -f "${d}user_profile.json" ]; then
            name=$(grep -o '"name": "[^"]*"' "${d}user_profile.json" 2>/dev/null | cut -d'"' -f4)
            niche=$(grep -o '"niche": "[^"]*"' "${d}user_profile.json" 2>/dev/null | cut -d'"' -f4)
            phone=$(grep -o '"phone": "[^"]*"' "${d}user_profile.json" 2>/dev/null | cut -d'"' -f4)
            echo "  📍 $name ($phone) — $niche"
            count=$((count+1))
        fi
    done
    echo "  Total: $count client(s)"
fi
echo ""
echo "💾 RAM:"
free -h | grep Mem
echo ""
echo "💽 Disque:"
df -h / | tail -1
echo ""
echo "✅ Done."
