#!/usr/bin/env bash
# =============================================================================
# @AsTech — Database Initialization Script
# Waits for PostgreSQL, applies schema, runs migration.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# ── Config ──────────────────────────────────────────────────────────────────
PG_HOST="${POSTGRES_HOST:-127.0.0.1}"
PG_PORT="${POSTGRES_PORT:-5432}"
PG_DB="${POSTGRES_DB:-astach}"
PG_USER="${POSTGRES_USER:-astach}"
PG_PASSWORD="${POSTGRES_PASSWORD:-astach_secret_2026}"
SCHEMA_FILE="$SCRIPT_DIR/db-schema.sql"
MIGRATE_SCRIPT="$SCRIPT_DIR/migrate-json-to-pg.py"

LOG_FILE="$PROJECT_DIR/logs/init-db.log"

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# ── Wait for PostgreSQL ─────────────────────────────────────────────────────
wait_for_postgres() {
    local max_attempts=60
    local attempt=1

    log "⏳ Waiting for PostgreSQL at ${PG_HOST}:${PG_PORT}..."

    # First try with pg_isready if available
    if command -v pg_isready &>/dev/null; then
        while ! pg_isready -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" &>/dev/null; do
            if [ "$attempt" -ge "$max_attempts" ]; then
                log "❌ PostgreSQL not ready after ${max_attempts} attempts."
                return 1
            fi
            sleep 2
            attempt=$((attempt + 1))
        done
    else
        # Fallback: try connecting via Python/psycopg2
        log "ℹ️  pg_isready not found, trying Python fallback..."
        while ! python3 -c "
import psycopg2
try:
    c = psycopg2.connect(host='$PG_HOST', port=$PG_PORT, dbname='$PG_DB', user='$PG_USER', password='$PG_PASSWORD')
    c.close()
    print('ok')
except Exception:
    print('no')
" 2>/dev/null | grep -q 'ok'; do
            if [ "$attempt" -ge "$max_attempts" ]; then
                log "❌ PostgreSQL not ready after ${max_attempts} attempts."
                return 1
            fi
            sleep 2
            attempt=$((attempt + 1))
        done
    fi

    log "✅ PostgreSQL is ready! (${attempt}s)"
    return 0
}

# ── Apply schema ────────────────────────────────────────────────────────────
apply_schema() {
    if [ ! -f "$SCHEMA_FILE" ]; then
        log "❌ Schema file not found: $SCHEMA_FILE"
        return 1
    fi

    log "📜 Applying database schema: $SCHEMA_FILE"

    # Use psql if available, else use Python/psycopg2
    if command -v psql &>/dev/null; then
        PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -f "$SCHEMA_FILE" 2>&1 | tee -a "$LOG_FILE"
    else
        log "ℹ️  psql not found, using Python to apply schema..."
        python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from db_layer import get_db

db = get_db()
try:
    db.connect()
    with open('$SCHEMA_FILE') as f:
        sql = f.read()
    # Split by semicolons and execute each statement
    for stmt in sql.split(';'):
        stmt = stmt.strip()
        if stmt and not stmt.startswith('--'):
            try:
                with db._cursor() as cur:
                    cur.execute(stmt)
            except Exception as e:
                if 'already exists' not in str(e).lower():
                    print(f'Warning: {e}')
    print('Schema applied successfully.')
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
finally:
    db.close()
" 2>&1 | tee -a "$LOG_FILE"
    fi

    log "✅ Schema applied!"
    return 0
}

# ── Run migration ───────────────────────────────────────────────────────────
run_migration() {
    if [ ! -f "$MIGRATE_SCRIPT" ]; then
        log "❌ Migration script not found: $MIGRATE_SCRIPT"
        return 1
    fi

    log "📦 Running JSON-to-PostgreSQL migration..."
    python3 "$MIGRATE_SCRIPT" 2>&1 | tee -a "$LOG_FILE"
    local rc=${PIPESTATUS[0]}

    if [ "$rc" -eq 0 ]; then
        log "✅ Migration completed successfully!"
    else
        log "⚠️  Migration completed with errors (exit code $rc)."
        log "   Check logs for details."
    fi

    return "$rc"
}

# ── Mark as initialized ─────────────────────────────────────────────────────
mark_initialized() {
    python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from db_layer import get_db

db = get_db()
try:
    db.connect()
    with db._cursor() as cur:
        cur.execute(
            \"INSERT INTO schema_version (version, description) VALUES ('init', 'Initialized by init-db.sh')\"
        )
    print('✅ Initialization marked in database.')
except Exception as e:
    print(f'⚠️  Could not mark initialization: {e}')
finally:
    db.close()
" 2>&1 | tee -a "$LOG_FILE"
}

# ── Main ────────────────────────────────────────────────────────────────────
main() {
    log "=" 60
    log "🚀 @AsTech — Database Initialization"
    log "=" 60
    log "Host: $PG_HOST:$PG_PORT"
    log "Database: $PG_DB"
    log "User: $PG_USER"

    # Check dependencies
    if ! python3 -c "import psycopg2" 2>/dev/null; then
        log "ℹ️  Installing psycopg2-binary..."
        pip install psycopg2-binary 2>&1 | tee -a "$LOG_FILE"
    fi

    wait_for_postgres || exit 1
    apply_schema || exit 1
    run_migration || true  # Don't exit on migration warnings
    mark_initialized

    log ""
    log "✅ @AsTech database initialization complete!"
    log "   Clients in DB: $(python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from db_layer import get_db
db = get_db()
try:
    db.connect()
    clients = db.get_all_clients()
    print(len(clients))
finally:
    db.close()
" 2>/dev/null || echo '?')"
}

main "$@"
