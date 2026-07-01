# Erfolgskriterien – Pilotphase @AsTech V3.0

**Pilotkunde:** Reinhardt & Kollegen Steuerberatungsgesellschaft mbH  
**Zeitraum:** 01.07.2026 – 31.07.2026 (30 Tage)

---

## Übersicht

Dieses Dokument definiert die messbaren Erfolgskriterien für die Pilotphase. Die Ergebnisse entscheiden darüber, ob der Kunde in den Professional-Plan (200 €/Monat) überführt wird und ob das Produkt für die breite Markteinführung bereit ist.

---

## 1. Nutzungsmetriken

| Kriterium | Zielwert | Minimum | Messmethode |
|-----------|----------|---------|-------------|
| **Anzahl Konversationen** | ≥ 100 | ≥ 50 | Logs im Proxy-System |
| **Aktive Tage** | ≥ 20 von 30 | ≥ 15 | Logs (≥1 Nachricht pro Tag) |
| **Anzahl der Fragen pro Tag** | ≥ 3 | ≥ 1 | Logs, Tagesdurchschnitt |
| **Genutzte Funktionen** | ≥ 4 von 7 | ≥ 3 | System-Logs (Feature-Tracking) |
| **Mandanten angelegt** | ≥ 5 | ≥ 3 | Datenbankeinträge |

---

## 2. Qualitätsmetriken

| Kriterium | Zielwert | Minimum | Messmethode |
|-----------|----------|---------|-------------|
| **Antwortzeit (Durchschnitt)** | ≤ 8 Sek. | ≤ 15 Sek. | Proxy-Logs (Zeitstempel) |
| **Antwortgenauigkeit** | ≥ 90 % | ≥ 85 % | Kundenbewertung (Stichprobe) |
| **Antworten auf Deutsch** | 100 % | 100 % | Automatische Spracherkennung |
| **Kontextverständnis** | ≥ 85 % | ≥ 75 % | Manuelle Auswertung (J+14, J+30) |
| **Halluzinationsrate** | ≤ 2 % | ≤ 5 % | Stichprobenprüfung durch Admin |

### Definition Antwortgenauigkeit

Die Genauigkeit wird durch **Stichproben** gemessen: Der Kunde bewertet 10 zufällig ausgewählte Antworten pro Woche auf einer Skala von 1–5:
- **5** = Vollständig korrekt, sofort verwendbar
- **4** = Kleinere Ungenauigkeiten, aber brauchbar
- **3** = Teilweise korrekt, Nachbearbeitung nötig
- **2** = Überwiegend falsch
- **1** = Völlig falsch / Halluzination

Eine Antwort gilt als „genau", wenn sie mit ≥ 4 bewertet wird.
Genauigkeit (%) = (Anzahl Antworten ≥ 4) / (Gesamtzahl bewertete Antworten) × 100

---

## 3. Kundenzufriedenheit

| Kriterium | Zielwert | Minimum | Messmethode |
|-----------|----------|---------|-------------|
| **Zufriedenheit Woche 1** | ≥ 4,0 / 5,0 | ≥ 3,0 / 5,0 | Direkte Abfrage (1–5) |
| **Zufriedenheit Woche 2** | ≥ 4,5 / 5,0 | ≥ 3,5 / 5,0 | Direkte Abfrage (1–5) |
| **Zufriedenheit Woche 3** | ≥ 4,5 / 5,0 | ≥ 4,0 / 5,0 | Direkte Abfrage (1–5) |
| **NPS (Woche 4)** | ≥ 50 | ≥ 40 | NPS-Umfrage (0–10) |
| **Weiterempfehlungsbereitschaft** | „Sehr wahrscheinlich" | „Wahrscheinlich" | Abschlussgespräch |

### NPS-Berechnung

NPS = % Promotoren (9–10) − % Detraktoren (0–6)
- **Promotoren** = Bewertung 9–10 → sehr zufrieden, werden weiterempfehlen
- **Passive** = Bewertung 7–8 → zufrieden, aber nicht begeistert
- **Detraktoren** = Bewertung 0–6 → unzufrieden, werden abraten

---

## 4. Stabilitätsmetriken

| Kriterium | Zielwert | Maximum | Messmethode |
|-----------|----------|---------|-------------|
| **Kritische Bugs** | 0 | 0 | Bug-Tracking |
| **Schwere Bugs** | 0 | 3 | Bug-Tracking |
| **Kosmetische Bugs** | ≤ 5 | ≤ 10 | Bug-Tracking |
| **Ausfallzeit** | ≤ 30 Min. | ≤ 120 Min. | Uptime-Monitoring |
| **Proxy-Verfügbarkeit** | ≥ 99,5 % | ≥ 99,0 % | Uptime-Monitoring |

### Bug-Klassifikation

| Stufe | Definition | Beispiel |
|-------|-----------|----------|
| **Kritisch** | Systemausfall, Datenverlust, Sicherheitslücke | Proxy antwortet nicht, Login unmöglich |
| **Schwer** | Hauptfunktion beeinträchtigt, kein Workaround | Falsche Steuerberechnung, Terminerinnerung fehlt |
| **Kosmetisch** | Kleinere UI-/UX-Probleme, Workaround vorhanden | Schriftgröße, falsche Formatierung |

---

## 5. Geschäftsmetriken

| Kriterium | Zielwert | Minimum | Messmethode |
|-----------|----------|---------|-------------|
| **Conversion zu Professional** | Ja | — | Vertragsabschluss |
| **Zahlungsbereitschaft** | 200 €/Monat | — | Angebot, Verhandlung |
| **Referenzbereitschaft** | Ja (Testimonial) | — | Abschlussgespräch |
| **Empfohlene Produktverbesserungen** | ≥ 3 konkrete Vorschläge | — | Feedback-Sammlung |

---

## 6. Ampelsystem – Gesamtbewertung

| Farbe | Status | Bedeutung | Entscheidung |
|-------|--------|-----------|-------------|
| 🟢 **Grün** | Alle Zielwerte erreicht | Produkt ist marktreif | → Professional-Plan anbieten, Launch vorbereiten |
| 🟡 **Gelb** | Mindestwerte erreicht, Zielwerte teilweise verfehlt | Produkt ist vielversprechend, Optimierung nötig | → Professional-Plan anbieten mit verlängerter Optimierungsphase |
| 🔴 **Rot** | Mindestwerte nicht erreicht | Produkt ist nicht bereit | → Kein Angebot, interne Überarbeitung, erneute Pilotphase |

---

## 7. Entscheidungsmatrix (J+30)

Trifft **mindestens eines** der folgenden Kriterien zu → **ROT**:

- [ ] NPS < 40
- [ ] Antwortgenauigkeit < 85 %
- [ ] Kritische Bugs aufgetreten
- [ ] Mehr als 3 schwere Bugs
- [ ] Kunde lehnt Professional-Plan ab
- [ ] Kunde bricht Testphase vorzeitig ab

Trifft **kein rotes** Kriterium zu → **GELB oder GRÜN** (abhängig von Zielwerten)

---

## 8. Dokumentation der Ergebnisse

Nach Abschluss der Testphase wird ein **Abschlussbericht** erstellt mit:

1. Metrik-Ergebnisse tabellarisch (Ist vs. Soll)
2. Gesammeltes Feedback (wörtliche Zitate)
3. Bug-Report (vollständige Liste)
4. NPS-Ergebnis
5. Ampelfarbe und Entscheidungsempfehlung
6. Nächste Schritte

---

*@AsTech V3.0 — Erfolgskriterien Pilotphase • Stand: Juli 2026*
