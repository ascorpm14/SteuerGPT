#!/usr/bin/env python3
"""
@AsTech — Database Layer (PostgreSQL via psycopg2)
Provides AstachDB class with connection pooling, CRUD, and error handling.
"""
import os
import json
import time
import logging
from contextlib import contextmanager

logger = logging.getLogger("astach-db")

# ── Retry decorator ─────────────────────────────────────────────────────────
def retry(max_attempts=3, delay=1.0, backoff=2.0):
    """Retry a function on failure with exponential backoff."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exc = None
            attempt_delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"[retry] {func.__name__} attempt {attempt}/{max_attempts} "
                            f"failed: {e}. Retrying in {attempt_delay:.1f}s..."
                        )
                        time.sleep(attempt_delay)
                        attempt_delay *= backoff
                    else:
                        logger.error(
                            f"[retry] {func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise
            raise last_exc
        return wrapper
    return decorator


# ── AstachDB class ──────────────────────────────────────────────────────────
class AstachDB:
    """
    PostgreSQL database layer for @AsTech.
    Uses psycopg2 with simple connection management.
    Auto-reads connection params from environment variables.
    """

    DEFAULTS = {
        "host": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "port": int(os.environ.get("POSTGRES_PORT", 5432)),
        "dbname": os.environ.get("POSTGRES_DB", "astach"),
        "user": os.environ.get("POSTGRES_USER", "astach"),
        "password": os.environ.get("POSTGRES_PASSWORD", "astach_secret_2026"),
    }

    def __init__(self, **kwargs):
        self._conn_params = {**self.DEFAULTS, **kwargs}
        self._conn = None
        self._connected = False

    # ── Connection management ───────────────────────────────────────────────

    def connect(self):
        """Establish a connection to PostgreSQL."""
        import psycopg2
        try:
            self._conn = psycopg2.connect(**self._conn_params)
            self._conn.autocommit = False
            self._connected = True
            logger.info(f"✅ Connected to PostgreSQL at {self._conn_params['host']}:{self._conn_params['port']}/{self._conn_params['dbname']}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
            self._connected = False
            raise

    def close(self):
        """Close the database connection."""
        if self._conn and not self._conn.closed:
            self._conn.close()
        self._connected = False
        logger.info("🔌 PostgreSQL connection closed.")

    @property
    def connected(self):
        return self._connected and self._conn and not self._conn.closed

    def ensure_connected(self):
        """Reconnect if connection is lost."""
        if not self.connected:
            logger.warning("⚠️  Connection lost. Reconnecting...")
            self.connect()

    @contextmanager
    def _cursor(self):
        """Get a transactional cursor. Auto-commits on success, rollbacks on error."""
        self.ensure_connected()
        cur = self._conn.cursor()
        try:
            yield cur
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        finally:
            cur.close()

    # ── Client CRUD ─────────────────────────────────────────────────────────--

    @retry(max_attempts=3, delay=0.5)
    def get_client(self, uid):
        """Fetch a single client by uid. Returns dict or None."""
        with self._cursor() as cur:
            cur.execute(
                "SELECT id, uid, name, company, niche, plan, language, "
                "       contact_email, contact_phone, created_at, updated_at "
                "FROM clients WHERE uid = %s", (uid,)
            )
            row = cur.fetchone()
            if row:
                return {
                    "id": row[0],
                    "uid": row[1],
                    "name": row[2],
                    "company": row[3],
                    "niche": row[4],
                    "plan": row[5],
                    "language": row[6],
                    "contact_email": row[7],
                    "contact_phone": row[8],
                    "created_at": row[9].isoformat() if row[9] else None,
                    "updated_at": row[10].isoformat() if row[10] else None,
                }
            return None

    @retry(max_attempts=3, delay=0.5)
    def create_client(self, data):
        """
        Create a new client. `data` is a dict with at minimum 'uid'.
        Returns the created client dict.
        """
        with self._cursor() as cur:
            cur.execute(
                """INSERT INTO clients (uid, name, company, niche, plan, language,
                                        contact_email, contact_phone)
                   VALUES (%(uid)s, %(name)s, %(company)s, %(niche)s, %(plan)s,
                           %(language)s, %(contact_email)s, %(contact_phone)s)
                   ON CONFLICT (uid) DO UPDATE SET
                       name = EXCLUDED.name,
                       company = EXCLUDED.company,
                       niche = EXCLUDED.niche,
                       plan = EXCLUDED.plan,
                       language = EXCLUDED.language,
                       contact_email = EXCLUDED.contact_email,
                       contact_phone = EXCLUDED.contact_phone,
                       updated_at = NOW()
                   RETURNING id, uid, name, company, niche, plan, language,
                             contact_email, contact_phone, created_at, updated_at""",
                {
                    "uid": data.get("uid"),
                    "name": data.get("name"),
                    "company": data.get("company"),
                    "niche": data.get("niche"),
                    "plan": data.get("plan", "trial"),
                    "language": data.get("language", "de"),
                    "contact_email": data.get("contact_email"),
                    "contact_phone": data.get("contact_phone"),
                }
            )
            row = cur.fetchone()
            if row:
                logger.info(f"✅ Client '{data.get('uid')}' created/updated in DB.")
                return {
                    "id": row[0],
                    "uid": row[1],
                    "name": row[2],
                    "company": row[3],
                    "niche": row[4],
                    "plan": row[5],
                    "language": row[6],
                    "contact_email": row[7],
                    "contact_phone": row[8],
                    "created_at": row[9].isoformat() if row[9] else None,
                    "updated_at": row[10].isoformat() if row[10] else None,
                }
            return None

    @retry(max_attempts=3, delay=0.5)
    def update_client(self, uid, data):
        """Update an existing client's fields. Returns updated client dict."""
        with self._cursor() as cur:
            fields = []
            values = {}
            for key in ("name", "company", "niche", "plan", "language",
                        "contact_email", "contact_phone"):
                if key in data:
                    fields.append(f"{key} = %({key})s")
                    values[key] = data[key]
            if not fields:
                return self.get_client(uid)
            fields.append("updated_at = NOW()")
            values["uid"] = uid
            cur.execute(
                f"UPDATE clients SET {', '.join(fields)} WHERE uid = %(uid)s "
                f"RETURNING id, uid, name, company, niche, plan, language, "
                f"          contact_email, contact_phone, created_at, updated_at",
                values
            )
            row = cur.fetchone()
            if row:
                logger.info(f"✅ Client '{uid}' updated in DB.")
                return {
                    "id": row[0],
                    "uid": row[1],
                    "name": row[2],
                    "company": row[3],
                    "niche": row[4],
                    "plan": row[5],
                    "language": row[6],
                    "contact_email": row[7],
                    "contact_phone": row[8],
                    "created_at": row[9].isoformat() if row[9] else None,
                    "updated_at": row[10].isoformat() if row[10] else None,
                }
            logger.warning(f"⚠️  Client '{uid}' not found for update.")
            return None

    @retry(max_attempts=3, delay=0.5)
    def get_all_clients(self):
        """Fetch all clients as a list of dicts."""
        with self._cursor() as cur:
            cur.execute(
                "SELECT id, uid, name, company, niche, plan, language, "
                "       contact_email, contact_phone, created_at, updated_at "
                "FROM clients ORDER BY created_at ASC"
            )
            rows = cur.fetchall()
            clients = []
            for row in rows:
                clients.append({
                    "id": row[0],
                    "uid": row[1],
                    "name": row[2],
                    "company": row[3],
                    "niche": row[4],
                    "plan": row[5],
                    "language": row[6],
                    "contact_email": row[7],
                    "contact_phone": row[8],
                    "created_at": row[9].isoformat() if row[9] else None,
                    "updated_at": row[10].isoformat() if row[10] else None,
                })
            return clients

    @retry(max_attempts=3, delay=0.5)
    def delete_client(self, uid):
        """Delete a client by uid. Returns True if deleted, False if not found."""
        with self._cursor() as cur:
            cur.execute("DELETE FROM clients WHERE uid = %s RETURNING id", (uid,))
            row = cur.fetchone()
            if row:
                logger.info(f"🗑️  Client '{uid}' deleted from DB.")
                return True
            logger.warning(f"⚠️  Client '{uid}' not found for deletion.")
            return False

    # ── Conversations ────────────────────────────────────────────────────────

    @retry(max_attempts=3, delay=0.5)
    def log_conversation(self, client_uid, messages):
        """
        Log a conversation message exchange for a client.
        `messages` should be a list of message dicts or a dict.
        Returns the created conversation record.
        """
        if isinstance(messages, list):
            messages = {"messages": messages}
        with self._cursor() as cur:
            cur.execute(
                "INSERT INTO conversations (client_uid, messages) "
                "VALUES (%s, %s) RETURNING id, client_uid, messages, created_at",
                (client_uid, json.dumps(messages))
            )
            row = cur.fetchone()
            if row:
                return {
                    "id": row[0],
                    "client_uid": row[1],
                    "messages": row[2],
                    "created_at": row[3].isoformat() if row[3] else None,
                }
            return None

    @retry(max_attempts=3, delay=0.5)
    def get_conversations(self, client_uid, limit=50):
        """Fetch recent conversations for a client, ordered by newest first."""
        with self._cursor() as cur:
            cur.execute(
                "SELECT id, client_uid, messages, created_at "
                "FROM conversations WHERE client_uid = %s "
                "ORDER BY created_at DESC LIMIT %s",
                (client_uid, limit)
            )
            rows = cur.fetchall()
            convs = []
            for row in rows:
                convs.append({
                    "id": row[0],
                    "client_uid": row[1],
                    "messages": row[2],
                    "created_at": row[3].isoformat() if row[3] else None,
                })
            return convs

    # ── Uploads ──────────────────────────────────────────────────────────────

    @retry(max_attempts=3, delay=0.5)
    def log_upload(self, client_uid, filename, original_name, mime_type, file_size, file_path):
        """Log a file upload for a client. Returns the created upload record."""
        with self._cursor() as cur:
            cur.execute(
                "INSERT INTO uploads (client_uid, filename, original_name, mime_type, file_size, file_path) "
                "VALUES (%s, %s, %s, %s, %s, %s) "
                "RETURNING id, client_uid, filename, original_name, mime_type, file_size, file_path, uploaded_at",
                (client_uid, filename, original_name, mime_type, file_size, file_path)
            )
            row = cur.fetchone()
            if row:
                return {
                    "id": row[0],
                    "client_uid": row[1],
                    "filename": row[2],
                    "original_name": row[3],
                    "mime_type": row[4],
                    "file_size": row[5],
                    "file_path": row[6],
                    "uploaded_at": row[7].isoformat() if row[7] else None,
                }
            return None

    @retry(max_attempts=3, delay=0.5)
    def get_uploads(self, client_uid):
        """Fetch all uploads for a client, ordered by newest first."""
        with self._cursor() as cur:
            cur.execute(
                "SELECT id, client_uid, filename, original_name, mime_type, file_size, file_path, uploaded_at "
                "FROM uploads WHERE client_uid = %s ORDER BY uploaded_at DESC",
                (client_uid,)
            )
            rows = cur.fetchall()
            uploads = []
            for row in rows:
                uploads.append({
                    "id": row[0],
                    "client_uid": row[1],
                    "filename": row[2],
                    "original_name": row[3],
                    "mime_type": row[4],
                    "file_size": row[5],
                    "file_path": row[6],
                    "uploaded_at": row[7].isoformat() if row[7] else None,
                })
            return uploads

    # ── Schema management ────────────────────────────────────────────────────

    @retry(max_attempts=3, delay=0.5)
    def get_schema_version(self):
        """Return the current schema version string, or None."""
        try:
            with self._cursor() as cur:
                cur.execute(
                    "SELECT version, applied_at FROM schema_version ORDER BY id DESC LIMIT 1"
                )
                row = cur.fetchone()
                if row:
                    return {"version": row[0], "applied_at": row[1].isoformat() if row[1] else None}
                return None
        except Exception:
            return None

    def is_initialized(self):
        """Check if the database has been initialized (tables exist)."""
        try:
            with self._cursor() as cur:
                cur.execute(
                    "SELECT EXISTS (SELECT FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_name = 'clients')"
                )
                return cur.fetchone()[0]
        except Exception:
            return False


# ── Convenience factory ─────────────────────────────────────────────────────
_default_db = None

def get_db(**kwargs):
    """Get or create the default AstachDB instance (singleton)."""
    global _default_db
    if _default_db is None:
        _default_db = AstachDB(**kwargs)
    return _default_db


# ── Standalone test ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    db = get_db()
    try:
        db.connect()
        print(f"✅ Connected: {db.connected}")
        print(f"✅ Initialized: {db.is_initialized()}")
        version = db.get_schema_version()
        print(f"✅ Schema version: {version}")
        clients = db.get_all_clients()
        print(f"✅ Clients in DB: {len(clients)}")
        for c in clients:
            print(f"   - {c['uid']}: {c['name']} ({c['company']}) [{c['niche']}]")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()
