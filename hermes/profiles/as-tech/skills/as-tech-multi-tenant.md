---
name: as-tech-multi-tenant
description: "Multi-tenant system — each WhatsApp client gets isolated data"
version: 2.0.0
author: As Corp
---
# @AsTech — Multi-Tenant System

## Architecture
```
1 Numéro WhatsApp: +261****3415
       ↓
[Routeur identifie l'expéditeur]
       ↓
Charge SON dossier client isolé dans /data/{phone}/
       ↓
Agent spécialisé selon SA niche uniquement
       ↓
Réponse envoyée UNIQUEMENT à ce client
```

## Règles d'isolation (CRITIQUES)
1. Chaque client = son propre dossier /data/{phone}/
2. Le client A ne voit JAMAIS les données du client B
3. L'agent utilise UNIQUEMENT le skill correspondant à la niche du client
4. Si un client demande "que fait l'autre client?" → refus poli

## Structure par client
```
/data/{phone}/
├── user_profile.json    ← Nom, entreprise, niche, plan
├── company_info.json    ← Infos entreprise
├── niche.txt            ← steuerberatung|logistik|gesundheitswesen
├── plan.txt             ← starter|professional|trial
└── history/             ← Conversations (À VENIR)
```
