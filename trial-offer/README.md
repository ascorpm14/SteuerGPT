# @AsTech V3.0 — Pack Pilote Client

> **Assistant IA professionnel pour cabinets de Steuerberatung (fiscalité/comptabilité allemande)**

---

## 📋 Contenu du pack

| Fichier | Description |
|---------|-------------|
| `pilot-client-profile.json` | Profil complet du client pilote (Dr. Anja Reinhardt, Reinhardt & Kollegen) |
| `trial-agreement-de.md` | Contrat d'essai professionnel en allemand, conforme DSGVO |
| `onboarding-checklist.md` | Checklist onboarding avec étapes, livrables et responsables |
| `kickoff-email-de.md` | Email de bienvenue en allemand (APK, identifiants, support) |
| `trial-setup.sh` | Script automatisé de création du dossier client dans le système JSON |
| `success-criteria.md` | Critères de succès mesurables (métriques, NPS, bugs, satisfaction) |
| `README.md` | Ce fichier — vue d'ensemble et instructions commerciales |

---

## 🚀 Instructions pour le commercial

### 1. Avant le kickoff

```bash
# Créer le dossier client dans le système
cd /root/steuergpt/trial-offer
./trial-setup.sh client_491726543210 "Dr. Anja Reinhardt" \
  "Reinhardt & Kollegen Steuerberatung" steuerberatung \
  reinhardt@reinhardt-steuer.de +491726543210
```

### 2. Préparer les livrables

- [ ] Générer l'APK personnalisée (voir documentation technique)
- [ ] Préparer le code d'accès unique
- [ ] Imprimer ou envoyer le contrat d'essai (`trial-agreement-de.md`)
- [ ] Planifier la session de démo (30–45 min)

### 3. Jour J — Kickoff

- [ ] Envoyer l'email de bienvenue (`kickoff-email-de.md`) avec le lien APK
- [ ] Faire signer le contrat d'essai (numériquement ou papier)
- [ ] Conduire la session de démo
- [ ] Vérifier techniquement que tout fonctionne

### 4. Suivi

| J+7  | Appel ou email — première impression, bugs éventuels |
|------|------------------------------------------------------|
| J+14 | Point détaillé — métriques, optimisation, satisfaction |
| J+21 | Bilan intermédiaire — préparation conversion |
| J+30 | Bilan final — décision Professional Plan (200€/mois) |

### 5. Après la phase pilote

- **Si conversion :** facturation, activation compte pro, intégration production
- **Si non-conversion :** désactivation, suppression des données sous 14 jours, remerciements

---

## 📊 Critères de succès (résumé)

| Métrique | Seuil minimum | Objectif |
|----------|---------------|----------|
| Conversations | ≥ 50 | ≥ 100 |
| Précision réponses | ≥ 85 % | ≥ 90 % |
| Temps de réponse | ≤ 15s | ≤ 8s |
| Bugs critiques | 0 | 0 |
| Bugs majeurs | ≤ 3 | 0 |
| NPS | ≥ 40 | ≥ 50 |
| Satisfaction client | ≥ 3,5/5 | ≥ 4,5/5 |

---

## 🛠️ Script de setup

Le script `trial-setup.sh` créé automatiquement :
- `user_profile.json`
- `company_info.json`
- `niche.txt`
- Entrée PostgreSQL (si disponible)

Usage :
```bash
./trial-setup.sh <client_uid> <client_name> <company> <niche> <email> <phone>
```

---

## 📝 Notes internes

- Client prioritaire : cabinet de 12 collaborateurs, fiscalité PME/indépendants
- Contact direct : Dr. Anja Reinhardt
- Canal d'acquisition : démarchage direct (outbound)
- Tarification post-trial : 200 €/mois (Professional Plan)
- Toute modification du pack doit être versionnée dans ce dossier

---

**@AsTech V3.0** — *votre assistant IA pour les cabinets de Steuerberatung allemands*  
Contact : ascorpm14@gmail.com | +261375959215  
Dernière mise à jour : juillet 2026
