#!/usr/bin/env bash
# =============================================================================
# @AsTech — Full Setup Script
# Orchestrates: Docker Compose up, database init, proxy restart.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

LOG_FILE="$PROJECT_DIR/logs/setup.log"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# ── Color helpers ───────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail()  { echo -e "${RED}[FAIL]${NC} $*"; }

# ── Banner ──────────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}          🚀 @AsTech — Full Setup with PostgreSQL           ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ── 1. Check prerequisites ─────────────────────────────────────────────────
info "🔍 Checking prerequisites..."

# Check Docker
if command -v docker &>/dev/null; then
    ok "Docker found: $(docker --version)"
else
    fail "Docker not found. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if docker compose version &>/dev/null; then
    ok "Docker Compose found: $(docker compose version)"
elif command -v docker-compose &>/dev/null; then
    ok "docker-compose found: $(docker-compose --version)"
    DOCKER_COMPOSE="docker-compose"
else
    fail "Docker Compose not found."
    exit 1
fi

# Check Python 3
if command -v python3 &>/dev/null; then
    ok "Python 3 found: $(python3 --version)"
else
    fail "Python 3 not found."
    exit 1
fi

# Check DEEPSEEK_API_KEY
if [ -z "${DEEPSEEK_API_KEY:-}" ]; then
    warn "DEEPSEEK_API_KEY env var not set."
    warn "The Hermes service may fail to start without it."
    warn "Set it with: export DEEPSEEK_API_KEY='your-key-here'"
else
    ok "DEEPSEEK_API_KEY is set"
fi

echo ""

# ── 2. Install Python dependencies ─────────────────────────────────────────
info "🐍 Installing Python dependencies..."
pip install psycopg2-binary 2>&1 | tee -a "$LOG_FILE" | tail -3
ok "Python dependencies installed."

# ── 3. Start Docker services ───────────────────────────────────────────────
info "🐳 Starting Docker services (PostgreSQL, n8n, Hermes)..."
cd "$PROJECT_DIR"

# Check if existing containers are running
if docker ps --format '{{.Names}}' | grep -q 'as-tech-postgres'; then
    warn "PostgreSQL already running."
else
    docker compose up -d as-tech-postgres 2>&1 | tee -a "$LOG_FILE" | tail -3
    ok "PostgreSQL container started (or already running)."
fi

# ── 4. Wait for PostgreSQL ─────────────────────────────────────────────────
info "⏳ Waiting for PostgreSQL to be ready..."
bash "$SCRIPT_DIR/init-db.sh" 2>&1 | tee -a "$LOG_FILE" | while IFS= read -r line; do
    echo "  $line"
done

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    ok "Database initialized successfully!"
else
    fail "Database initialization failed. Check $LOG_FILE for details."
    exit 1
fi

# ── 5. Start remaining services ─────────────────────────────────────────────
info "🐳 Starting n8n and Hermes..."
docker compose up -d 2>&1 | tee -a "$LOG_FILE" | tail -3
ok "All Docker services started."

# ── 6. Start/restart the multi-tenant proxy ─────────────────────────────────
info "🔌 Starting multi-tenant proxy (port 8090)..."

# Check if proxy is already running on port 8090
PROXY_PID=$(lsof -ti:8090 2>/dev/null || true)
if [ -n "$PROXY_PID" ]; then
    warn "Proxy already running on port 8090 (PID: $PROXY_PID). Restarting..."
    kill "$PROXY_PID" 2>/dev/null || true
    sleep 1
fi

# Start the proxy with DB_FIRST enabled
cd "$PROJECT_DIR"
nohup python3 scripts/multi-tenant-proxy.py > "$PROJECT_DIR/logs/proxy.log" 2>&1 &
PROXY_PID=$!
echo $PROXY_PID > "$PROJECT_DIR/logs/proxy.pid"
sleep 2

if kill -0 "$PROXY_PID" 2>/dev/null; then
    ok "Multi-tenant proxy started (PID: $PROXY_PID)"
else
    fail "Proxy failed to start. Check $PROJECT_DIR/logs/proxy.log"
fi

# ── 7. Health check ─────────────────────────────────────────────────────────
info "🏥 Running health checks..."
sleep 2

# Check PostgreSQL
if docker exec as-tech-postgres pg_isready -U astach -d astach &>/dev/null; then
    ok "PostgreSQL is healthy"
else
    warn "PostgreSQL health check failed"
fi

# Check Proxy
if curl -sf http://127.0.0.1:8090/health > /dev/null 2>&1; then
    ok "Multi-tenant proxy is healthy (port 8090)"
    curl -s http://127.0.0.1:8090/health 2>/dev/null | python3 -m json.tool 2>/dev/null || true
else
    warn "Proxy health check failed (may need more time to start)"
fi

# Check n8n
if curl -sf http://127.0.0.1:5678/healthz > /dev/null 2>&1; then
    ok "n8n is healthy (port 5678)"
else
    warn "n8n health check failed (may need more time to start)"
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}          ✅ @AsTech Setup Complete!                         ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${CYAN}PostgreSQL:${NC}     127.0.0.1:5432 (astach/astach_secret_2026)"
echo -e "  ${CYAN}Multi-tenant Proxy:${NC}  http://127.0.0.1:8090"
echo -e "  ${CYAN}n8n:${NC}              http://127.0.0.1:5678"
echo -e "  ${CYAN}Hermes:${NC}           127.0.0.1:8081 (via proxy)"
echo ""
echo -e "  ${YELLOW}Logs:${NC}"
echo -e "    Setup log:    $LOG_FILE"
echo -e "    Proxy log:    $PROJECT_DIR/logs/proxy.log"
echo -e "    DB init log:  $PROJECT_DIR/logs/init-db.log"
echo ""
