-- ============================================================================
-- @AsTech — PostgreSQL Schema
-- Database: astach
-- ============================================================================

-- ── Clients table ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS clients (
    id              SERIAL PRIMARY KEY,
    uid             VARCHAR(255) UNIQUE NOT NULL,
    name            VARCHAR(255),
    company         VARCHAR(255),
    niche           VARCHAR(255),
    plan            VARCHAR(50) DEFAULT 'trial',
    language        VARCHAR(10) DEFAULT 'de',
    contact_email   VARCHAR(255),
    contact_phone   VARCHAR(50),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clients_uid ON clients(uid);

-- ── Conversations table ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS conversations (
    id              SERIAL PRIMARY KEY,
    client_uid      VARCHAR(255) NOT NULL REFERENCES clients(uid) ON DELETE CASCADE,
    messages        JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_client_uid ON conversations(client_uid);

-- ── Uploads table ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS uploads (
    id              SERIAL PRIMARY KEY,
    client_uid      VARCHAR(255) NOT NULL REFERENCES clients(uid) ON DELETE CASCADE,
    filename        VARCHAR(255),
    original_name   VARCHAR(255),
    mime_type       VARCHAR(255),
    file_size       BIGINT,
    file_path       VARCHAR(1024),
    uploaded_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_uploads_client_uid ON uploads(client_uid);

-- ── Migration tracking ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS schema_version (
    id              SERIAL PRIMARY KEY,
    version         VARCHAR(50) NOT NULL UNIQUE,
    applied_at      TIMESTAMPTZ DEFAULT NOW(),
    description     TEXT
);

INSERT INTO schema_version (version, description)
VALUES ('1.0', 'Initial schema: clients, conversations, uploads')
ON CONFLICT DO NOTHING;
