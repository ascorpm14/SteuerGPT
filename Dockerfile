# ═══════════════════════════════════════════════════════════════
#  @AsTech — Docker Container (FINAL)
#  Hermes Agent + WhatsApp Gateway + n8n
#  Model: DeepSeek V4 Flash (API)
# ═══════════════════════════════════════════════════════════════
FROM python:3.11

ENV HERMES_HOME=/etc/hermes \
    NODE_PATH=/usr/lib/node_modules

# ── System deps ──────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git build-essential ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# ── Node.js 20 + WhatsApp bridge + Chromium ──────────────────
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs chromium \
    && npm install -g whatsapp-web.js@latest

# ── Hermes Agent ─────────────────────────────────────────────
RUN pip install --upgrade pip \
    && git clone https://github.com/NousResearch/hermes-agent.git /opt/hermes-source \
    && cd /opt/hermes-source \
    && pip install -e ".[all]"

RUN echo '#!/bin/bash\npython3 -m hermes_cli.main "$@"' > /usr/local/bin/hermes \
    && chmod +x /usr/local/bin/hermes

# ── Dirs & Config ───────────────────────────────────────────
RUN mkdir -p ${HERMES_HOME}/{profiles/as-tech/{skills,memories,sessions},data,logs}
COPY hermes/config.yaml ${HERMES_HOME}/config.yaml
COPY hermes/profiles/as-tech/config.yaml ${HERMES_HOME}/profiles/as-tech/config.yaml
COPY hermes/profiles/as-tech/skills/ ${HERMES_HOME}/profiles/as-tech/skills/
COPY scripts/entrypoint.sh /entrypoint.sh
COPY scripts/init-hermes.py /opt/hermes-source/init-hermes.py
COPY scripts/generate-qr.js /opt/hermes-source/generate-qr.js
RUN chmod +x /entrypoint.sh

VOLUME ["${HERMES_HOME}/data", "${HERMES_HOME}/logs", \
        "${HERMES_HOME}/profiles/as-tech/memories"]

ENTRYPOINT ["/entrypoint.sh"]
