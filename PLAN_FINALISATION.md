# @AsTech — Plan de finalisation produit

## Architecture cible
```
1 Container Unique
├── Hermes Gateway (1 connexion WhatsApp = +261****3415)
├── Multi-tenant routeur (n8n)
│   ├── Identifie expéditeur → charge son dossier
│   └── Aiguille vers le bon contexte
├── Clients/
│   ├── {numero}/
│   │   ├── user_profile.json    ← Données du client
│   │   ├── company_info.json    ← Infos entreprise
│   │   ├── niche.txt            ← steuerberatung|logistik|gesundheit
│   │   ├── plan.txt             ← starter|professional
│   │   ├── conversations/       ← Historique
│   │   └── files/               ← Documents clients
│   └── ...
└── Skills/
    ├── as-tech-multi-tenant.md  ← Routage + isolation
    ├── as-tech-steuerberatung.md
    ├── as-tech-logistik.md
    └── as-tech-gesundheitswesen.md
```

## PLAN D'EXÉCUTION

### Phase 1 — Infrastructure multi-tenant (Agent 1)
- Objectif : Rendre le système capable de gérer N clients isolés
- Fichiers à créer :
  - /root/steuergpt/scripts/multi-tenant-router.js (routeur Node.js)
  - /root/steuergpt/hermes/profiles/as-tech/data/ (dossier clients)
  - Script de création de client : /root/steuergpt/scripts/add-client.py
- Ce que ça fait :
  - Quand un numéro inconnu écrit → créer son dossier client
  - Quand un client connu écrit → charger son contexte
  - Les données d'un client ne sont jamais accessibles par un autre

### Phase 2 — WhatsApp persistent (Agent 2)
- Objectif : Connexion WhatsApp stable qui survit aux redémarrages
- Actions :
  - Configurer le client WhatsApp avec session persistante
  - Générer code d'appairage final
  - Configurer auto-reconnect
  - Sauvegarder la session dans un volume Docker persistant

### Phase 3 — n8n workflows (Agent 3)
- Objectif : Middleware de routage intelligent
- Créer :
  - Workflow "Message entrant" → identifie client → route
  - Workflow "Nouveau client" → notification à l'admin
  - Workflow "Cron client A" → tâches programmées par client

### Phase 4 — Scripts de déploiement (Agent 4)
- Objectif : Automatiser l'ajout de nouveaux clients
- Créer :
  - /root/steuergpt/scripts/deploy-client.sh
  - /root/steuergpt/scripts/backup-client.sh
  - /root/steuergpt/scripts/healthcheck.sh
  - README.md avec instructions de déploiement

### Phase 5 — Tests & Validation (Agent 5)
- Objectif : Vérifier que tout fonctionne
- Tester :
  - Créer 2 clients fictifs (Weber + Bauer)
  - Vérifier que Weber voit pas les données de Bauer
  - Vérifier que le bon skill est chargé selon la niche
  - Vérifier que le gateway démarre sans erreur
