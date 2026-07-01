#!/usr/bin/env python3
"""@AsTech — Add a new client with isolated data directory + PostgreSQL."""
import os, json, sys, argparse

DATA_DIR = "/root/steuergpt/hermes/profiles/as-tech/data"

# Try to import db_layer for PostgreSQL sync
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from db_layer import get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

def create_client(phone, name, company, niche, plan="trial"):
    uid = phone.replace('+', '').replace(' ', '')
    client_dir = os.path.join(DATA_DIR, f"client_{uid}")
    os.makedirs(client_dir, exist_ok=True)
    os.chmod(client_dir, 0o700)
    
    profile = {
        "phone": phone, "name": name, "company": company,
        "niche": niche, "plan": plan, "language": "de",
        "trial_start": None, "onboarded": False
    }
    with open(os.path.join(client_dir, "user_profile.json"), "w") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    
    with open(os.path.join(client_dir, "niche.txt"), "w") as f:
        f.write(niche + "\n")
    
    info = {"company": company, "phone": phone, "industry": niche}
    with open(os.path.join(client_dir, "company_info.json"), "w") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    
    # ── Sync to PostgreSQL if available ──────────────────────────────────────
    if DB_AVAILABLE:
        try:
            db = get_db()
            db.connect()
            db.create_client({
                "uid": uid,
                "name": name,
                "company": company,
                "niche": niche,
                "plan": plan,
                "language": "de",
                "contact_phone": phone,
            })
            db.close()
            print(f"   ✅ Synchronisé dans PostgreSQL")
        except Exception as e:
            print(f"   ⚠️  Échec synchro PostgreSQL: {e}")
    
    print(f"✅ Client créé : {name} ({company})")
    print(f"   Téléphone : {phone}")
    print(f"   Niche : {niche}")
    print(f"   Plan : {plan}")
    print(f"   Dossier : {client_dir}")
    return client_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="@AsTech — Ajouter un client")
    parser.add_argument("--phone", required=True, help="Numéro WhatsApp du client")
    parser.add_argument("--name", required=True, help="Nom du contact")
    parser.add_argument("--company", required=True, help="Nom de l'entreprise")
    parser.add_argument("--niche", required=True, choices=["steuerberatung","logistik","gesundheitswesen"])
    parser.add_argument("--plan", default="trial", choices=["trial","starter","professional"])
    args = parser.parse_args()
    create_client(args.phone, args.name, args.company, args.niche, args.plan)
