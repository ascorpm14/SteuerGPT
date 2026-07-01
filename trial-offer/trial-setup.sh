#!/usr/bin/env bash
#=============================================================================
# @AsTech V3.0 — trial-setup.sh
# Client-Pilot-Setup: Erstellt Client-Dossier im bestehenden JSON-System
# und optional in PostgreSQL.
#
# Usage:
#   ./trial-setup.sh <client_uid> <client_name> <company> <niche> <email> <phone>
#
# Beispiel:
#   ./trial-setup.sh client_491726543210 "Dr. Anja Reinhardt" \
#     "Reinhardt & Kollegen Steuerberatung" steuerberatung \
#     reinhardt@reinhardt-steuer.de +491726543210
#=============================================================================

set -euo pipefail

# === Configuration ===
DATA_DIR="/root/steuergpt/hermes/profiles/as-tech/data"
TRIAL_DURATION_DAYS=30

# === Colors ===
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# === Args ===
if [ $# -lt 6 ]; then
    echo -e "${RED}❌ Usage: $0 <client_uid> <client_name> <company> <niche> <email> <phone>${NC}"
    echo ""
    echo "  client_uid  : Eindeutige Client-ID (z. B. client_491726543210)"
    echo "  client_name : Vollständiger Name des Ansprechpartners"
    echo "  company     : Firmenname"
    echo "  niche       : Branche (steuerberatung | logistik | gesundheitswesen)"
    echo "  email       : E-Mail-Adresse"
    echo "  phone       : Telefonnummer inkl. Ländervorwahl"
    exit 1
fi

CLIENT_UID="$1"
CLIENT_NAME="$2"
COMPANY="$3"
NICHE="$4"
EMAIL="$5"
PHONE="$6"

# === Validate niche ===
VALID_NICHES=("steuerberatung" "logistik" "gesundheitswesen")
NICHE_OK=false
for n in "${VALID_NICHES[@]}"; do
    if [ "$n" = "$NICHE" ]; then
        NICHE_OK=true
        break
    fi
done
if [ "$NICHE_OK" = false ]; then
    echo -e "${RED}❌ Ungültige Niche '$NICHE'. Erlaubt: ${VALID_NICHES[*]}${NC}"
    exit 1
fi

echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  @AsTech V3.0 — Trial Client Setup${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${YELLOW}Client UID:${NC}    $CLIENT_UID"
echo -e "  ${YELLOW}Name:${NC}          $CLIENT_NAME"
echo -e "  ${YELLOW}Company:${NC}       $COMPANY"
echo -e "  ${YELLOW}Niche:${NC}         $NICHE"
echo -e "  ${YELLOW}Email:${NC}         $EMAIL"
echo -e "  ${YELLOW}Phone:${NC}         $PHONE"
echo ""

# === Step 1: Create client directory ===
CLIENT_DIR="${DATA_DIR}/${CLIENT_UID}"
echo -e "${YELLOW}[1/5]${NC} Erstelle Client-Verzeichnis: ${CLIENT_DIR}"
mkdir -p "$CLIENT_DIR"
chmod 700 "$CLIENT_DIR"
echo -e "  ${GREEN}✅${NC} Verzeichnis erstellt: $CLIENT_DIR"

# === Step 2: Create user_profile.json ===
TRIAL_START=$(date +%Y-%m-%d)
TRIAL_END=$(date -d "+${TRIAL_DURATION_DAYS} days" +%Y-%m-%d)

echo -e "${YELLOW}[2/5]${NC} Erstelle user_profile.json..."
cat > "${CLIENT_DIR}/user_profile.json" << EOF
{
  "phone": "$PHONE",
  "name": "$CLIENT_NAME",
  "company": "$COMPANY",
  "niche": "$NICHE",
  "plan": "trial",
  "language": "de",
  "trial_start": "$TRIAL_START",
  "trial_end": "$TRIAL_END",
  "onboarded": false
}
EOF
echo -e "  ${GREEN}✅${NC} user_profile.json erstellt"
echo -e "  ${GREEN}   Trial-Zeitraum: ${TRIAL_START} bis ${TRIAL_END}${NC}"

# === Step 3: Create niche.txt ===
echo -e "${YELLOW}[3/5]${NC} Erstelle niche.txt..."
echo "$NICHE" > "${CLIENT_DIR}/niche.txt"
echo -e "  ${GREEN}✅${NC} niche.txt erstellt (Inhalt: $NICHE)"

# === Step 4: Create company_info.json ===
echo -e "${YELLOW}[4/5]${NC} Erstelle company_info.json..."
cat > "${CLIENT_DIR}/company_info.json" << EOF
{
  "company": "$COMPANY",
  "phone": "$PHONE",
  "email": "$EMAIL",
  "industry": "$NICHE",
  "trial": true,
  "trial_start": "$TRIAL_START",
  "trial_end": "$TRIAL_END"
}
EOF
echo -e "  ${GREEN}✅${NC} company_info.json erstellt"

# === Step 5: PostgreSQL insert (if available) ===
echo -e "${YELLOW}[5/5]${NC} Versuche PostgreSQL-Eintrag..."
if command -v psql &> /dev/null; then
    # Check if PostgreSQL is reachable
    if pg_isready -q 2>/dev/null; then
        # Try to insert — creates table if not exists
        psql -d astech -c "
            CREATE TABLE IF NOT EXISTS clients (
                client_uid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                company TEXT NOT NULL,
                niche TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                plan TEXT DEFAULT 'trial',
                trial_start DATE,
                trial_end DATE,
                onboarded BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW()
            );
        " 2>/dev/null || echo -e "  ${YELLOW}⚠️  Tabelle konnte nicht erstellt werden (keine Berechtigung oder DB fehlt)${NC}"

        psql -d astech -c "
            INSERT INTO clients (client_uid, name, company, niche, email, phone, plan, trial_start, trial_end)
            VALUES ('$CLIENT_UID', '$CLIENT_NAME', '$COMPANY', '$NICHE', '$EMAIL', '$PHONE', 'trial', '$TRIAL_START', '$TRIAL_END')
            ON CONFLICT (client_uid) DO UPDATE SET
                name = EXCLUDED.name,
                company = EXCLUDED.company,
                niche = EXCLUDED.niche,
                email = EXCLUDED.email,
                phone = EXCLUDED.phone,
                trial_start = EXCLUDED.trial_start,
                trial_end = EXCLUDED.trial_end;
        " 2>/dev/null && echo -e "  ${GREEN}✅${NC} PostgreSQL-Eintrag erfolgreich" \
                     || echo -e "  ${YELLOW}⚠️  PostgreSQL nicht verfügbar oder keine DB 'astech' vorhanden${NC}"
    else
        echo -e "  ${YELLOW}⚠️  PostgreSQL-Server nicht erreichbar. Nur JSON-Dateien erstellt.${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠️  psql nicht installiert. Nur JSON-Dateien erstellt.${NC}"
fi

# === Summary ===
echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Client erfolgreich eingerichtet!${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Client:     $CLIENT_NAME"
echo -e "  Firma:      $COMPANY"
echo -e "  UID:        $CLIENT_UID"
echo -e "  Verzeichnis: ${CLIENT_DIR}"
echo -e "  Trial:      ${TRIAL_START} → ${TRIAL_END} (${TRIAL_DURATION_DAYS} Tage)"
echo ""
echo -e "  ${CYAN}Dateien:${NC}"
ls -la "${CLIENT_DIR}/"
echo ""
echo -e "  ${YELLOW}Nächste Schritte:${NC}"
echo -e "  1. Personalisierte APK generieren"
echo -e "  2. Kickoff-E-Mail senden (Vorlage: kickoff-email-de.md)"
echo -e "  3. Demosession durchführen"
echo -e "  4. Onboarding-Checkliste abarbeiten"
echo ""

exit 0
