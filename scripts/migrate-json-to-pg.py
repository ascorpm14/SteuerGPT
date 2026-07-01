#!/usr/bin/env python3
"""
@AsTech — Migrate JSON data files to PostgreSQL.
Reads all client_* folders from the data directory, parses JSONs,
and inserts/upserts them into the astach database.
"""
import os
import sys
import json
import logging

# Ensure we can import db_layer from the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_layer import AstachDB, get_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("migrate-json-to-pg")

DATA_DIR = os.environ.get(
    "CLIENTS_DIR",
    "/root/steuergpt/hermes/profiles/as-tech/data"
)
ARCHIVE_DIR = os.path.join(DATA_DIR, ".migrated")


def get_client_uid_from_folder(folder_name):
    """
    Derive the client UID from the folder name.
    Folder format: client_{uid} → uid
    If folder has no 'client_' prefix, use folder name as-is.
    """
    if folder_name.startswith("client_"):
        return folder_name[7:]
    return folder_name


def parse_profile(profile_path):
    """Parse user_profile.json and extract migratable fields."""
    try:
        with open(profile_path) as f:
            data = json.load(f)

        # Determine UID: use 'uid' field if present, otherwise derive from folder
        uid = data.get("uid", "")
        phone = data.get("phone", data.get("contact_phone", ""))
        email = data.get("email", data.get("contact_email", ""))

        return {
            "uid": uid,
            "name": data.get("name", ""),
            "company": data.get("company", ""),
            "niche": data.get("niche", ""),
            "plan": data.get("plan", "trial"),
            "language": data.get("language", "de"),
            "contact_email": email,
            "contact_phone": phone,
            "_raw": data,
        }
    except Exception as e:
        logger.error(f"  ❌ Failed to parse {profile_path}: {e}")
        return None


def parse_company_info(info_path):
    """Parse company_info.json for additional metadata."""
    try:
        if not os.path.exists(info_path):
            return {}
        with open(info_path) as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"  ⚠️  Failed to parse {info_path}: {e}")
        return {}


def parse_niche(niche_path):
    """Read niche from niche.txt."""
    try:
        if not os.path.exists(niche_path):
            return ""
        with open(niche_path) as f:
            return f.read().strip()
    except Exception as e:
        logger.warning(f"  ⚠️  Failed to read {niche_path}: {e}")
        return ""


def archive_folder(client_dir, folder_name):
    """Move the client folder to the .migrated archive directory."""
    try:
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        dest = os.path.join(ARCHIVE_DIR, folder_name)
        os.rename(client_dir, dest)
        logger.info(f"  📦 Archived to {dest}")
        return True
    except Exception as e:
        logger.warning(f"  ⚠️  Could not archive {client_dir}: {e}")
        return False


def main():
    logger.info("=" * 60)
    logger.info("🚀 @AsTech — JSON to PostgreSQL Migration")
    logger.info("=" * 60)

    if not os.path.isdir(DATA_DIR):
        logger.error(f"❌ Data directory not found: {DATA_DIR}")
        sys.exit(1)

    # ── Connect to database ──────────────────────────────────────────────────
    db = get_db()
    try:
        db.connect()
        logger.info(f"✅ Connected to PostgreSQL: {db.connected}")
    except Exception as e:
        logger.error(f"❌ Cannot connect to PostgreSQL: {e}")
        logger.error("   Make sure PostgreSQL is running and accessible.")
        sys.exit(1)

    if not db.is_initialized():
        logger.error("❌ Database not initialized (tables missing). Run db-schema.sql first.")
        sys.exit(1)

    # ── Scan client folders ──────────────────────────────────────────────────
    client_folders = sorted([
        d for d in os.listdir(DATA_DIR)
        if d.startswith("client_") and os.path.isdir(os.path.join(DATA_DIR, d))
    ])

    if not client_folders:
        logger.warning("⚠️  No client folders found to migrate.")
        # Show what's in DATA_DIR
        all_items = os.listdir(DATA_DIR)
        logger.info(f"   Contents of {DATA_DIR}: {all_items}")
        sys.exit(0)

    logger.info(f"📂 Found {len(client_folders)} client folders to process")

    stats = {"success": 0, "skipped": 0, "errors": 0, "total": len(client_folders)}

    for folder_name in client_folders:
        client_dir = os.path.join(DATA_DIR, folder_name)
        uid_from_folder = get_client_uid_from_folder(folder_name)

        logger.info(f"\n📁 Processing: {folder_name} (uid={uid_from_folder})")

        # Parse profile
        profile_path = os.path.join(client_dir, "user_profile.json")
        if not os.path.exists(profile_path):
            logger.warning(f"  ⚠️  No user_profile.json found — skipping")
            stats["skipped"] += 1
            continue

        profile = parse_profile(profile_path)
        if profile is None:
            stats["errors"] += 1
            continue

        # If no UID in profile, use the folder-derived UID
        if not profile["uid"]:
            profile["uid"] = uid_from_folder
            logger.info(f"  ℹ️  Using folder-derived UID: {uid_from_folder}")

        # Read niche from niche.txt if not already in profile
        if not profile["niche"]:
            niche_path = os.path.join(client_dir, "niche.txt")
            profile["niche"] = parse_niche(niche_path)
        if not profile["niche"]:
            profile["niche"] = "allgemein"

        # Merge company_info data
        info_path = os.path.join(client_dir, "company_info.json")
        company_info = parse_company_info(info_path)
        if company_info:
            if not profile.get("company"):
                profile["company"] = company_info.get("company", "")
            if not profile.get("contact_phone"):
                profile["contact_phone"] = company_info.get("phone", "")
            if not profile.get("contact_email"):
                profile["contact_email"] = company_info.get("email", "")

        # Insert/upsert into database
        try:
            result = db.create_client({
                "uid": profile["uid"],
                "name": profile.get("name", ""),
                "company": profile.get("company", ""),
                "niche": profile.get("niche", "allgemein"),
                "plan": profile.get("plan", "trial"),
                "language": profile.get("language", "de"),
                "contact_email": profile.get("contact_email"),
                "contact_phone": profile.get("contact_phone"),
            })
            if result:
                logger.info(f"  ✅ Migrated: {profile['uid']} → {result['name']} ({result['company']})")
                stats["success"] += 1

                # Optionally archive the folder
                archive = os.environ.get("MIGRATE_ARCHIVE", "true").lower() == "true"
                if archive:
                    archive_folder(client_dir, folder_name)
            else:
                logger.warning(f"  ⚠️  No result from upsert for {profile['uid']}")
                stats["skipped"] += 1
        except Exception as e:
            logger.error(f"  ❌ DB error for {profile['uid']}: {e}")
            stats["errors"] += 1

    # ── Summary ──────────────────────────────────────────────────────────────
    logger.info("\n" + "=" * 60)
    logger.info("📊 Migration Summary")
    logger.info("=" * 60)
    logger.info(f"   Total folders:  {stats['total']}")
    logger.info(f"   ✅ Migrated:    {stats['success']}")
    logger.info(f"   ⏭️  Skipped:     {stats['skipped']}")
    logger.info(f"   ❌ Errors:      {stats['errors']}")

    # List all clients in DB now
    logger.info("\n📋 Clients in PostgreSQL:")
    all_clients = db.get_all_clients()
    for c in all_clients:
        logger.info(f"   · {c['uid']}: {c['name']} ({c['company']}) — {c['niche']} [{c['plan']}]")

    db.close()
    logger.info("\n✅ Migration complete!")

    return 0 if stats["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
