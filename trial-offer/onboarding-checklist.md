# Onboarding-Checkliste – Pilotkunde @AsTech V3.0

**Kunde:** Reinhardt & Kollegen Steuerberatungsgesellschaft mbH  
**Kontakt:** Dr. Anja Reinhardt (+491726543210)  
**Start:** 01.07.2026 | **Ende:** 31.07.2026  
**Verantwortlich:** @AsTech Team (Ascorp M.)

---

## Phase 1: Einrichtung (Vor dem Start)

### ☐ 1.1 Client-Dossier in der Datenbank anlegen
- **Aktionen:**
  - Neues Client-Verzeichnis erstellen: `client_491726543210/`
  - `user_profile.json` mit vollständigen Daten schreiben
  - `company_info.json` erstellen
  - `niche.txt` mit Inhalt `steuerberatung` anlegen
  - PostgreSQL-Eintrag (falls verfügbar) hinzufügen
- **Lieferbar:** Initialisierte Client-Daten auf dem Server
- **Verantwortlich:** Admin @AsTech
- **Erledigt:** ☐ | Datum: \_\_\_\_\_\_\_

### ☐ 1.2 Personalisierte APK generieren
- **Aktionen:**
  - APK mit Client-spezifischem Proxy-Endpunkt (Port 8090) bauen
  - APK signieren (letzter Build-Zertifikat verwenden)
  - APK auf sicheren Download-Server hochladen
- **Lieferbar:** `Reinhardt-Steuerberatung-v1.0.apk` (signiert)
- **Verantwortlich:** Admin @AsTech
- **Erledigt:** ☐ | Datum: \_\_\_\_\_\_\_

### ☐ 1.3 Zugangsdaten und Dokumentation vorbereiten
- **Aktionen:**
  - Einmaligen Zugangscode für die App generieren
  - Kurzanleitung (deutsch) als PDF erstellen
  - FAQ-Blatt mit den häufigsten Fragen vorbereiten
- **Lieferbar:** Zugangscode + PDF-Dokumentation
- **Verantwortlich:** Admin @AsTech
- **Erledigt:** ☐ | Datum: \_\_\_\_\_\_\_

---

## Phase 2: Kickoff (Tag 1 — 01.07.2026)

### ☐ 2.1 Willkommens-E-Mail versenden
- **Aktionen:**
  - Personalisierte E-Mail an Dr. Reinhardt senden
  - APK-Download-Link beifügen
  - Zugangscode und Anleitung mitsenden
  - Support-E-Mail und Telefonnummer angeben
- **Lieferbar:** Gesendete E-Mail (CC an interne Ablage)
- **Verantwortlich:** Commercial @AsTech
- **Erledigt:** ☐ | Datum: \_\_\_\_\_\_\_

### ☐ 2.2 Demosession (30–45 Minuten)
- **Aktionen:**
  - Videocall via Teams/Zoom (Termin mit Dr. Reinhardt abstimmen)
  - Installation der APK auf dem Testgerät demonstrieren
  - Grundfunktionen vorführen: WhatsApp-Anfrage, Wissensbasis, Terminerinnerung
  - Erste Testfragen gemeinsam durchgehen
  - Offene Fragen klären
- **Lieferbar:** Durchgeführte Session mit Protokoll
- **Verantwortlich:** Commercial @AsTech + Admin @AsTech
- **Erledigt:** ☐ | Datum: \_\_\_\_\_\_\_

### ☐ 2.3 Technische Verifikation
- **Aktionen:**
  - Prüfen, ob die App auf dem Gerät des Kunden läuft
  - Proxy-Konnektivität testen (Port 8090)
  - Erste Nachricht im System loggen
- **Lieferbar:** Technisch funktionsfähige Verbindung bestätigt
- **Verantwortlich:** Admin @AsTech
- **Erledigt:** ☐ | Datum: \_\_\_\_\_\_\_

---

## Phase 3: Begleitung (Tage 2–29)

### ☐ 3.1 Follow-up J+7 (08.07.2026)
- **Aktionen:**
  - Telefonat oder E-Mail: Wie läuft die erste Woche?
  - Anzahl der bisherigen Konversationen prüfen (Ziel: >10)
  - Eventuelle Bugs oder Verbesserungswünsche aufnehmen
  - Kurze Zufriedenheitsabfrage (Skala 1–5)
- **Lieferbar:** Statusbericht nach Woche 1
- **Verantwortlich:** Commercial @AsTech
- **Erledigt:** ☐ | Datum: \_\_\_\_\_\_\_

### ☐ 3.2 Follow-up J+14 (15.07.2026)
- **Aktionen:**
  - Telefonat (15 min): Vertiefte Nutzung besprechen
  - Metriken analysieren: Konversationen, Antwortzeiten, Genauigkeit
  - Anpassungen am Modell oder Prompt vornehmen falls nötig
  - Zweite Zufriedenheitsabfrage
- **Lieferbar:** Optimierungsreport + Metriken
- **Verantwortlich:** Admin @AsTech + Commercial @AsTech
- **Erledigt:** ☐ | Datum: \_\_\_\_\_\_\_

### ☐ 3.3 Follow-up J+21 (22.07.2026)
- **Aktionen:**
  - E-Mail mit Zwischenbilanz der Testphase
  - NPS-Umfrage vorbereiten (Wie wahrscheinlich Weiterempfehlung?)
  - Vorgespräch über Post-Trial-Vertrag (Professional-Plan)
  - Offene Punkte aus den vorherigen Follow-ups klären
- **Lieferbar:** Zwischenbilanz + NPS-Vorabfrage
- **Verantwortlich:** Commercial @AsTech
- **Erledigt:** ☐ | Datum: \_\_\_\_\_\_\_

---

## Phase 4: Abschluss (Tag 30 — 31.07.2026)

### ☐ 4.1 Bilanzgespräch J+30
- **Aktionen:**
  - Abschlussgespräch (30 min, Videocall)
  - Vollständige Metriken präsentieren:
    - Anzahl Konversationen
    - Durchschnittliche Antwortzeit
    - Genauigkeit der Antworten (vom Kunden bewertet)
    - Anzahl Bugs (kritisch/major/minor)
    - NPS-Score
  - Gesamteindruck des Kunden einholen
  - Entscheidung: Wechsel in den Professional-Plan (200 €/Monat)?
- **Lieferbar:** Abschlussbericht + Entscheidungsdokument
- **Verantwortlich:** Admin @AsTech + Commercial @AsTech
- **Erledigt:** ☐ | Datum: \_\_\_\_\_\_\_

### ☐ 4.2 Post-Trial-Aktionen
- **Wenn Kunde wechselt:**
  - Rechnung für Professional-Plan erstellen
  - Zugang für Production-Setup konfigurieren
  - SLA-Dokument übergeben
  - Onboarding in den regulären Betrieb
- **Wenn Kunde nicht wechselt:**
  - Datenlöschung innerhalb von 14 Tagen einleiten
  - APK-Zugang deaktivieren
  - Dankschreiben senden
  - Feedback-Dokument für interne Verbesserungen archivieren
- **Lieferbar:** Vertrag (bei Wechsel) / Löschbestätigung (bei Abgabe)
- **Verantwortlich:** Admin @AsTech + Commercial @AsTech
- **Erledigt:** ☐ | Datum: \_\_\_\_\_\_\_

---

## Zusammenfassung Meilensteine

| Meilenstein | Datum | Verantwortlich | Status |
|-------------|-------|----------------|--------|
| Client-Dossier anlegen | Vor 01.07. | Admin | ☐ |
| APK generieren | Vor 01.07. | Admin | ☐ |
| Kickoff-E-Mail | 01.07. | Commercial | ☐ |
| Demosession | 01.07. | Beide | ☐ |
| J+7 Follow-up | 08.07. | Commercial | ☐ |
| J+14 Follow-up | 15.07. | Beide | ☐ |
| J+21 Follow-up | 22.07. | Commercial | ☐ |
| Abschluss J+30 | 31.07. | Beide | ☐ |

---

*@AsTech V3.0 — Onboarding Pilotkunde • Stand: Juli 2026*
