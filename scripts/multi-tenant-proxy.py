#!/usr/bin/env python3
"""
@AsTech — Multi-Tenant Routing Proxy
Sits between APK clients and Hermes API.
Routes by X-Client-ID to isolated client folders.
Supports PostgreSQL as primary data source with JSON fallback.
"""
import os, sys, json, time, uuid, re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError

# Add scripts dir to path so we can import db_layer
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

HERMES_API = os.environ.get("HERMES_API", "http://127.0.0.1:8081")
HERMES_KEY = os.environ.get("HERMES_KEY", "hermes-android-secret-key-2026")
CLIENTS_DIR = os.environ.get("CLIENTS_DIR", "/root/steuergpt/hermes/profiles/as-tech/data")
PROXY_PORT = int(os.environ.get("PROXY_PORT", "8090"))
UPLOAD_SERVICE = os.environ.get("UPLOAD_SERVICE", "http://127.0.0.1:8084")
DB_FIRST = os.environ.get("DB_FIRST", "true").lower() == "true"

os.makedirs(CLIENTS_DIR, exist_ok=True)

# ── Database connection (lazy) ──────────────────────────────────────────────
_db_instance = None

def get_db():
    """Get or create the database connection."""
    global _db_instance
    if _db_instance is None:
        try:
            from db_layer import get_db as _get_db
            _db_instance = _get_db()
            _db_instance.connect()
            print(f"[PROXY] ✅ PostgreSQL connected (DB_FIRST={DB_FIRST})")
        except Exception as e:
            print(f"[PROXY] ⚠️  PostgreSQL not available: {e}")
            print(f"[PROXY]    Falling back to JSON files only.")
            _db_instance = False  # Sentinal: don't retry
    return _db_instance if _db_instance else None

def load_client(uid):
    """Load a client's data. Tries DB first (if DB_FIRST), falls back to JSON files."""
    # Normalize: strip 'client_' prefix if user already included it
    normalized = uid
    if normalized.startswith("client_"):
        normalized = normalized[7:]
    
    # ── Try PostgreSQL first ──────────────────────────────────────────────────
    if DB_FIRST:
        db = get_db()
        if db and db.connected:
            try:
                client_row = db.get_client(normalized)
                if client_row:
                    data = {
                        "uid": normalized,
                        "source": "postgresql",
                        "profile": {
                            "uid": client_row.get("uid", normalized),
                            "name": client_row.get("name", "Unbekannt"),
                            "company": client_row.get("company", ""),
                            "niche": client_row.get("niche", "allgemein"),
                            "plan": client_row.get("plan", "trial"),
                            "language": client_row.get("language", "de"),
                            "contact_email": client_row.get("contact_email", ""),
                            "contact_phone": client_row.get("contact_phone", ""),
                        },
                        "niche": client_row.get("niche", "allgemein"),
                        "company": {
                            "company": client_row.get("company", ""),
                            "contact": client_row.get("contact_email", ""),
                        },
                    }
                    print(f"[PROXY] ✅ Loaded '{normalized}' from PostgreSQL")
                    return data
            except Exception as e:
                print(f"[PROXY] ⚠️  DB lookup failed for '{normalized}': {e}")
                print(f"[PROXY]    Falling back to JSON...")
    
    # ── Fallback: JSON files ──────────────────────────────────────────────────
    client_dir = os.path.join(CLIENTS_DIR, f"client_{normalized}")
    if not os.path.isdir(client_dir):
        client_dir = os.path.join(CLIENTS_DIR, normalized)
        if not os.path.isdir(client_dir):
            return None
    
    data = {"uid": normalized, "dir": client_dir, "source": "json"}
    
    # Load profile
    profile_path = os.path.join(client_dir, "user_profile.json")
    if os.path.exists(profile_path):
        with open(profile_path) as f:
            data["profile"] = json.load(f)
    
    # Load niche
    niche_path = os.path.join(client_dir, "niche.txt")
    if os.path.exists(niche_path):
        data["niche"] = open(niche_path).read().strip()
    
    # Load company info
    info_path = os.path.join(client_dir, "company_info.json")
    if os.path.exists(info_path):
        with open(info_path) as f:
            data["company"] = json.load(f)
    
    print(f"[PROXY] ✅ Loaded '{normalized}' from JSON files")
    return data

def build_client_context(client_data):
    """Build a system prompt that includes the client's context."""
    profile = client_data.get("profile", {})
    niche = client_data.get("niche", "allgemein")
    company = client_data.get("company", {})
    
    parts = [
        f"Du bist **@AsTech**, ein professioneller KI-Assistent für deutsche Unternehmen.",
        f"",
        f"## Dein aktueller Kunde",
        f"- Name: {profile.get('name', 'Unbekannt')}",
        f"- Unternehmen: {profile.get('company', 'Unbekannt')}",
        f"- Branche: {profile.get('niche', niche)}",
        f"- Plan: {profile.get('plan', 'trial')}",
        f"- Sprache: {profile.get('language', 'de')}",
    ]
    
    if company:
        parts.append(f"\n## Unternehmensinformationen")
        for k, v in company.items():
            parts.append(f"- {k}: {v}")
    
    parts.append(f"""
## WICHTIGE REGELN
1. Du arbeitest NUR für DIESEN Kunden ({profile.get('name', 'Kunde')}).
2. Du hast KEINEN Zugriff auf Daten anderer Kunden.
3. Wenn der Kunde nach anderen Kunden fragt → höflich ablehnen.
4. Speichere KEINE Daten von diesem Kunden ausserhalb seines Dossiers.
5. Antworte professionell auf Deutsch (Sie-Form).
""")
    
    # Load niche-specific context
    niche_skill_path = f"/root/steuergpt/hermes/profiles/as-tech/skills/as-tech-{niche}.md"
    if os.path.exists(niche_skill_path):
        with open(niche_skill_path) as f:
            skill_content = f.read()
            parts.append(f"\n## Fachkenntnisse ({niche})\n{skill_content}")
    
    return "\n".join(parts)

class MultiTenantHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        print(f"[PROXY] {self.client_address[0]} - {format % args}")
    
    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error(self, status, message):
        self._send_json(status, {"error": message})
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Client-ID")
        self.end_headers()
    
    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok", "service": "as-tech-multi-tenant-proxy", "version": "3.0"})
            return
        elif self.path.startswith("/api/download-per-client/"):
            # Serve APK hardcoded for a specific client
            client_id = self.path.split("/api/download-per-client/")[-1]
            # Strip any trailing slash
            client_id = client_id.rstrip("/")
            # Try exact match first, then with client_ prefix
            candidates = [
                f"/root/uploads/apk/astech-{client_id}.apk",
                f"/root/uploads/apk/astech-client_{client_id}.apk",
            ]
            found = None
            for c in candidates:
                if os.path.exists(c):
                    found = c
                    break
            if found:
                filename = os.path.basename(found)
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.android.package-archive")
                self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("X-Client-ID", client_id)
                self.end_headers()
                with open(found, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self._send_error(404, f"No APK found for client: {client_id}")
            return
        elif self.path.startswith("/api/download/"):
            # Serve APK download locally
            filename = self.path.split("/api/download/")[-1]
            filepath = f"/root/uploads/apk/{filename}"
            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.android.package-archive")
                self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self._send_error(404, f"File not found: {filename}")
            return
        elif self.path.startswith("/api/"):
            # Generic proxy for reports, cron-jobs, etc.
            self._proxy_get(f"{HERMES_API}{self.path}")
            return
        elif self.path == "/v1/models":
            self._proxy_get(f"{HERMES_API}/v1/models")
            return
        
        self._send_error(404, "Not found")
    
    def _proxy_get(self, target_url):
        """Proxy a GET request to the target URL."""
        try:
            headers = {"Authorization": f"Bearer {HERMES_KEY}"}
            # Forward X-Client-ID if present
            cid = self.headers.get("X-Client-ID", "")
            if cid:
                headers["X-Client-ID"] = cid
            
            req = Request(target_url, headers=headers)
            resp = urlopen(req, timeout=30)
            self.send_response(resp.status)
            self.send_header("Content-Type", resp.headers.get("Content-Type", "application/octet-stream"))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(resp.read())
        except Exception as e:
            self._send_error(502, f"Backend error: {e}")
    
    def do_POST(self):
        # Read body
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len > 0 else b"{}"
        
        # Extract client_id from header
        client_id = self.headers.get("X-Client-ID", "").strip()
        
        # Normalize: if client_id contains email or phone, use as-is
        if not client_id:
            # Try from body
            try:
                parsed = json.loads(body)
                client_id = parsed.get("client_id", "").strip()
            except:
                pass
        
        if not client_id:
            self._send_error(400, "X-Client-ID header required")
            return
        
        # Load client data
        client = load_client(client_id)
        if not client:
            self._send_error(403, f"Client '{client_id}' not found. Contact admin.")
            return
        
        if self.path == "/v1/chat/completions":
            self._handle_chat(client, body)
        elif self.path == "/api/upload":
            self._handle_upload(client, body, content_len)
        else:
            self._send_error(404, "Not found")
    
    def _handle_chat(self, client, raw_body):
        try:
            parsed = json.loads(raw_body)
        except:
            self._send_error(400, "Invalid JSON body")
            return
        
        # Build client-specific system context
        client_context = build_client_context(client)
        
        # Find system message in the messages array and prepend/replace
        messages = parsed.get("messages", [])
        has_system = False
        for msg in messages:
            if msg.get("role") == "system":
                msg["content"] = client_context + "\n\n" + msg["content"]
                has_system = True
                break
        
        if not has_system:
            messages.insert(0, {"role": "system", "content": client_context})
        
        parsed["messages"] = messages
        parsed["model"] = parsed.get("model", "deepseek-v4-flash")
        
        # Log the routing
        name = client.get("profile", {}).get("name", "Unknown")
        niche = client.get("niche", "unknown")
        print(f"[PROXY] Routing chat for {name} ({client['uid']}) - niche: {niche}")
        
        # Forward to Hermes
        try:
            req = Request(f"{HERMES_API}/v1/chat/completions", 
                         data=json.dumps(parsed).encode(),
                         headers={
                             "Content-Type": "application/json",
                             "Authorization": f"Bearer {HERMES_KEY}"
                         })
            resp = urlopen(req, timeout=120)
            self.send_response(resp.status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("X-Client-ID", client["uid"])
            self.send_header("X-Client-Name", name)
            self.end_headers()
            
            response_data = json.loads(resp.read())
            # Add client metadata to response
            response_data["_client"] = {
                "id": client["uid"],
                "name": name,
                "niche": niche
            }
            self.wfile.write(json.dumps(response_data).encode())
            
        except URLError as e:
            self._send_error(502, f"Hermes API error: {e.reason}")
        except Exception as e:
            self._send_error(500, f"Proxy error: {e}")
    
    def _handle_upload(self, client, raw_body, content_len):
        # Forward upload to upload service with client context
        name = client.get("profile", {}).get("name", "Unknown")
        print(f"[PROXY] Routing upload for {name} ({client['uid']})")
        
        try:
            req = Request(f"{UPLOAD_SERVICE}/api/upload",
                         data=raw_body,
                         headers={
                             "Content-Type": self.headers.get("Content-Type", "application/octet-stream"),
                             "X-Client-ID": client["uid"],
                         })
            resp = urlopen(req, timeout=60)
            self.send_response(resp.status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(resp.read())
        except Exception as e:
            self._send_error(502, f"Upload error: {e}")


def main():
    server = HTTPServer(("0.0.0.0", PROXY_PORT), MultiTenantHandler)
    print(f"[PROXY] @AsTech Multi-Tenant Proxy running on port {PROXY_PORT}")
    print(f"[PROXY] Routing to Hermes API: {HERMES_API}")
    print(f"[PROXY] Clients directory: {CLIENTS_DIR}")
    print(f"[PROXY] Upload service: {UPLOAD_SERVICE}")
    
    # Create default admin client if it doesn't exist
    admin_dir = os.path.join(CLIENTS_DIR, "client_admin")
    if not os.path.isdir(admin_dir):
        os.makedirs(admin_dir, exist_ok=True)
        with open(os.path.join(admin_dir, "user_profile.json"), "w") as f:
            json.dump({
                "uid": "admin",
                "name": "Admin As Corp",
                "company": "As Corp",
                "niche": "steuerberatung",
                "plan": "professional",
                "language": "fr"
            }, f, indent=2, ensure_ascii=False)
        with open(os.path.join(admin_dir, "niche.txt"), "w") as f:
            f.write("steuerberatung\n")
        print(f"[PROXY] ✅ Admin client created at {admin_dir}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[PROXY] Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
