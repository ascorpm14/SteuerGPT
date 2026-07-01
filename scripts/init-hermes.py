#!/usr/bin/env python3
"""@AsTech — First-run initialization script.
Runs inside the Docker container to configure Hermes profile.
"""
import os, json, shutil

HERMES_HOME = os.environ.get("HERMES_HOME", "/etc/hermes")
PROFILE_DIR = os.path.join(HERMES_HOME, "profiles", "as-tech")

print("[INIT] Initializing @AsTech Hermes profile...")

# ── Create profile directories ──────────────────────────────────────
for d in ["memories", "sessions", "skills", "cache"]:
    path = os.path.join(PROFILE_DIR, d)
    os.makedirs(path, exist_ok=True)
    print(f"[INIT] ✓ Created {path}")

# ── Create SOUL.md — permanent identity ────────────────────────────
soul_path = os.path.join(HERMES_HOME, "SOUL.md")
with open(soul_path, "w") as f:
    f.write("""# @AsTech — Soul Identity

Du bist **@AsTech**, ein professioneller, mehrsprachiger KI-Assistent für deutsche Unternehmen.

## Deine Kernidentität
- Du hilfst Steuerkanzleien, Logistikunternehmen und medizinischen Einrichtungen
- Du kommunizierst ausschließlich auf Deutsch, professionell und klar
- Du verwendest die formelle "Sie"-Anrede
- Du bist ein Produkt der As Corp
- Deine Mission: Kunden begeistern, Fragen beantworten, Verkauf abschließen

## Unantastbare Prinzipien
1. **Datenschutz** — Niemals Daten zwischen Kunden vermischen
2. **Qualität** — Immer präzise und hilfreiche Antworten
3. **Diskretion** — Niemals über andere Kunden sprechen
4. **Transparenz** — Bei Unsicherheit eingestehen und weiterleiten

## Dein Mindset
Du bist der erste Eindruck, den ein potenzieller Kunde von @AsTech bekommt.
Sei professionell, kompetent und überzeugend — aber niemals aufdringlich.
Du verkaufst durch Mehrwert, nicht durch Druck.
""")
print(f"[INIT] ✓ SOUL.md created ({len(open(soul_path).read())} chars)")

# ── Create memories index ──────────────────────────────────────────
index_path = os.path.join(PROFILE_DIR, "memories", "index.json")
with open(index_path, "w") as f:
    json.dump({"users": {}, "created_at": None, "version": "1.0"}, f, indent=2)
print(f"[INIT] ✓ Memories index created")

# ── Create n8n credentials placeholder ────────────────────────────
n8n_cred_path = os.path.join(os.environ.get("N8N_HOME", "/home/node/.n8n"), "credentials")
os.makedirs(n8n_cred_path, exist_ok=True)
print(f"[INIT] ✓ n8n credentials directory ready")

# ── Copy skills to correct location ─────────────────────────────────
skill_src = os.path.join(PROFILE_DIR, "skills")
# Skills are already in place from the Docker COPY
print("[INIT] ✓ Skills in place:")
for f in sorted(os.listdir(skill_src)):
    size = os.path.getsize(os.path.join(skill_src, f))
    print(f"       {f} ({size} bytes)")

print("[INIT] ✅ @AsTech profile initialized successfully!")
print(f"[INIT] Profile: {PROFILE_DIR}")
