#!/usr/bin/env bash
# =============================================================================
# @AsTech — Build APK per client with hardcoded client_id
# Usage: ./build-per-client.sh <client_id>
# Example: ./build-per-client.sh client_corp123
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="/root/android-app"
UPLOAD_DIR="/root/uploads/apk"
KEYSTORE="${KEYSTORE:-/root/android-app/keystore.jks}"
KEYSTORE_PASS="${KEYSTORE_PASS:-android}"
KEY_ALIAS="${KEY_ALIAS:-hermes}"
KEY_PASS="${KEY_PASS:-android}"

if [ $# -lt 1 ]; then
    echo "❌ Usage: $0 <client_id>"
    echo "   Example: $0 client_corp123"
    exit 1
fi

CLIENT_ID="$1"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
APK_OUTPUT="astech-${CLIENT_ID}-${TIMESTAMP}.apk"
APK_FINAL="astech-${CLIENT_ID}.apk"

echo "=============================================="
echo "  @AsTech — Build APK for client: ${CLIENT_ID}"
echo "=============================================="

# Step 1: Clean previous build
echo ""
echo "📦 Step 1/5 — Cleaning previous build..."
cd "$PROJECT_DIR"
./gradlew clean > /dev/null 2>&1 || true

# Step 2: Build release APK with hardcoded client_id
echo ""
echo "🔨 Step 2/5 — Building release APK (clientId=${CLIENT_ID})..."
./gradlew assembleRelease -PclientId="${CLIENT_ID}" --no-daemon 2>&1 | tail -20

BUILD_RESULT="${PIPESTATUS[0]}"
if [ "$BUILD_RESULT" -ne 0 ]; then
    echo "❌ Build failed (exit code $BUILD_RESULT)"
    exit $BUILD_RESULT
fi

# Locate the built APK
BUILT_APK=$(find "$PROJECT_DIR/app/build/outputs/apk/release" -name "*.apk" 2>/dev/null | head -1)
if [ -z "$BUILT_APK" ]; then
    echo "❌ No APK found in build output!"
    exit 1
fi
echo "✅ APK built: ${BUILT_APK}"

# Step 3: Sign the APK
echo ""
echo "✍️  Step 3/5 — Signing APK..."

# Check if keystore exists; if not, create a debug one
if [ ! -f "$KEYSTORE" ]; then
    echo "⚠️  Keystore not found at ${KEYSTORE}, generating a debug keystore..."
    keytool -genkey -v -keystore "$KEYSTORE" \
        -alias "$KEY_ALIAS" \
        -keyalg RSA -keysize 2048 -validity 10000 \
        -storepass "$KEYSTORE_PASS" \
        -keypass "$KEY_PASS" \
        -dname "CN=AsTech, OU=Dev, O=AsCorp, L=Paris, ST=Paris, C=FR" \
        -noprompt 2>/dev/null
    echo "✅ Debug keystore created"
fi

# Sign with apksigner (preferred) or jarsigner
SIGNED_APK="${BUILT_APK}.signed"
if command -v apksigner &>/dev/null; then
    apksigner sign \
        --ks "$KEYSTORE" \
        --ks-pass "pass:${KEYSTORE_PASS}" \
        --ks-key-alias "$KEY_ALIAS" \
        --key-pass "pass:${KEY_PASS}" \
        --out "$SIGNED_APK" \
        "$BUILT_APK" 2>&1
    mv "$SIGNED_APK" "$BUILT_APK"
    echo "✅ APK signed with apksigner"
elif command -v jarsigner &>/dev/null; then
    jarsigner -verbose \
        -keystore "$KEYSTORE" \
        -storepass "$KEYSTORE_PASS" \
        -keypass "$KEY_PASS" \
        -signedjar "$SIGNED_APK" \
        "$BUILT_APK" "$KEY_ALIAS" 2>&1
    mv "$SIGNED_APK" "$BUILT_APK"
    echo "✅ APK signed with jarsigner"
else
    echo "⚠️  No signing tool found (apksigner/jarsigner). Copying unsigned APK."
fi

# Step 4: Copy to uploads
echo ""
echo "📋 Step 4/5 — Copying to uploads..."
mkdir -p "$UPLOAD_DIR"
cp "$BUILT_APK" "${UPLOAD_DIR}/${APK_FINAL}"
cp "${BUILT_APK}" "${UPLOAD_DIR}/${APK_OUTPUT}"
echo "✅ Copied to: ${UPLOAD_DIR}/${APK_FINAL}"
echo "✅ Also saved: ${UPLOAD_DIR}/${APK_OUTPUT}"

# Step 5: Show metadata
echo ""
echo "📊 Step 5/5 — APK Metadata:"
APK_SIZE=$(stat --format=%s "${UPLOAD_DIR}/${APK_FINAL}" 2>/dev/null || stat -f%z "${UPLOAD_DIR}/${APK_FINAL}" 2>/dev/null)
APK_SIZE_MB=$(awk "BEGIN {printf \"%.1f\", ${APK_SIZE}/1048576}")
echo "  File:       ${APK_FINAL}"
echo "  Size:       ${APK_SIZE_MB} MB (${APK_SIZE} bytes)"
echo "  Client ID:  ${CLIENT_ID}"
echo "  Built:      $(date '+%Y-%m-%d %H:%M:%S')"

# Show the hardcoded client_id inside the APK (via aapt if available)
if command -v aapt &>/dev/null; then
    echo "  BuildConfig: $(aapt dump badging "${UPLOAD_DIR}/${APK_FINAL}" 2>/dev/null | grep -o "package: name='[^']*'" | head -1)"
elif command -v aapt2 &>/dev/null; then
    echo "  Package:    $(aapt2 dump packagename "${UPLOAD_DIR}/${APK_FINAL}" 2>/dev/null || echo 'N/A')"
fi

echo ""
echo "=============================================="
echo "  ✅ Build complete for client: ${CLIENT_ID}"
echo "  📱 APK ready: ${UPLOAD_DIR}/${APK_FINAL}"
echo "=============================================="
