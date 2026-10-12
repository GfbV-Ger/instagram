# GfbV-Linkseite für Instagram

Die Link-in-Bio-Seite der Gesellschaft für bedrohte Völker. Sie zeigt die neuesten Instagram-Beiträge von @bedrohtevoelker als Bilderraster. Jede Kachel führt zum passenden Inhalt auf gfbv.de.

Die Seite aktualisiert sich selbst: Alle zwei Stunden holt GitHub neue Posts ab, speichert das Titelbild, liest Titel und Link aus der Caption und veröffentlicht die Seite neu. Im Alltag muss niemand etwas tun außer posten.

---

## Was im Projekt liegt

| Ordner / Datei | Inhalt |
|---|---|
| `site/` | Die Seite selbst: `index.html`, Logo, Schrift Aller, Bilder, `beitraege.json` (die Liste der Beiträge) |
| `skript/aktualisieren.py` | Holt neue Posts von Instagram und schreibt `beitraege.json` |
| `skript/korrekturen.json` | Titel oder Link einzelner Beiträge von Hand korrigieren oder Beiträge ausblenden |
| `skript/manuell.json` | Beiträge, die das Skript nicht selbst findet (z. B. Kooperationsposts anderer Accounts) |
| `skript/einstellungen.json` | Anzahl der Kacheln, maximale Titellänge, Ersatzlink |
| `einrichtung/workflow-aktualisieren.yml` | Der Zeitplan für GitHub. Wird bei der Einrichtung einmal eingefügt (Schritt 4) |

---

## Einrichtung

### Phase 1 – Seite bei GitHub online bringen (ca. 25 Min.)

**Schritt 2 · GitHub-Organisation anlegen (10 Min.)**
1. Unter [github.com/signup](https://github.com/signup) ein Konto mit einer GfbV-Funktionsadresse anlegen (z. B. kommunikation@…), nicht mit einer privaten Adresse.
2. Oben rechts auf das Profilbild → **Your organizations** → **New organization** → Tarif **Free**.
3. Name z. B. `gfbv-ev`. Er taucht in der vorläufigen Adresse auf: `gfbv-ev.github.io/…`.
4. Weitere Kolleg*innen können später unter **People** eingeladen werden, damit die Seite nicht an einer Person hängt.

**Schritt 3 · Projekt anlegen und Dateien hochladen (5 Min.)**
1. In der Organisation: **Repositories** → **New repository**.
2. Name: `instagram`, Sichtbarkeit: **Public**. Häkchen bei „Add a README file“ setzen. **Create repository**.
3. Im neuen Projekt: **Add file** → **Upload files**.
4. Den entpackten Ordner `gfbv-linkseite` öffnen, **alle Inhalte** markieren (die Ordner `site`, `skript`, `einrichtung` und `README.md`) und ins Browserfenster ziehen. Die Ordnerstruktur bleibt erhalten.
5. Unten **Commit changes**. Die vorhandene README wird dabei durch diese Anleitung ersetzt.

**Schritt 4 · GitHub Pages einschalten und Zeitplan einfügen (5 Min.)**
1. Im Projekt: **Settings** → links **Pages** → unter „Build and deployment“ bei **Source** die Option **GitHub Actions** wählen. Weiter muss hier nichts eingestellt werden.
2. Oben auf **Actions** → **set up a workflow yourself**.
3. Als Dateinamen `aktualisieren.yml` eintragen (der Pfad `.github/workflows/` steht schon davor).
4. Den gesamten Inhalt von `einrichtung/workflow-aktualisieren.yml` kopieren und in das Editorfeld einfügen. Was dort vorher stand, vollständig ersetzen.
5. **Commit changes** → **Commit changes**.

Die Reihenfolge ist wichtig: erst Pages auf „GitHub Actions“ stellen, dann den Zeitplan einfügen.

**Schritt 5 · Seite prüfen (5 Min.)**
1. Unter **Actions** läuft jetzt „Beiträge aktualisieren“. Nach etwa einer Minute erscheint ein grüner Haken.
2. Im Lauf steht beim Schritt „Neue Instagram-Beiträge abrufen“ der Hinweis *„Kein Instagram-Zugangsschlüssel hinterlegt. Abruf übersprungen.“* Das ist richtig so, der Schlüssel kommt in Phase 2.
3. Die Adresse der Seite steht unter **Settings** → **Pages** („Your site is live at …“), z. B. `https://gfbv-ev.github.io/instagram/`. Auf Handy und Desktop öffnen.

Ab hier ist die Seite online, mit den 11 bereits eingetragenen Beiträgen.

---

### Phase 2 – Mit Instagram verknüpfen (ca. 1 Std.)

Hier wird ein Zugangsschlüssel erzeugt, mit dem GitHub die Posts lesen darf. Er wird über die Facebook-Seite der GfbV erzeugt, weil ein solcher Seiten-Schlüssel **nicht abläuft**.

Die Bezeichnungen in Metas Oberflächen ändern sich gelegentlich. Wenn ein Knopf anders heißt, nach dem sinngemäßen Begriff suchen.

**Schritt 6 · Instagram-Konto prüfen (5 Min.)**
1. In der Instagram-App unter **Einstellungen** → **Kontotyp und Tools** prüfen, dass @bedrohtevoelker ein **professionelles Konto** ist (Business oder Creator, nicht Privat).
2. Prüfen, dass das Konto mit der **Facebook-Seite der GfbV** verbunden ist: in der Instagram-App unter Profil → **Profil bearbeiten** → **Seite**, oder in der Meta Business Suite.
3. Du brauchst auf der Facebook-Seite **volle Kontrolle** bzw. Admin-Rechte.

**Schritt 7 · Meta-Entwicklerkonto und App anlegen (20 Min.)**
1. [developers.facebook.com](https://developers.facebook.com) öffnen, mit dem Facebook-Konto anmelden, das Admin der GfbV-Seite ist, und sich als Entwickler*in registrieren (Telefonnummer wird bestätigt).
2. **Meine Apps** → **App erstellen**.
3. Als Anwendungsfall **Andere** wählen, als App-Typ **Business**.
4. Name z. B. `GfbV Linkseite`, Kontakt-E-Mail eintragen, **App erstellen**.
5. Die App bleibt im Modus **Entwicklung**. Eine Prüfung durch Meta ist nicht nötig, weil die App nur Daten eures eigenen Kontos liest.

**Schritt 8 · Zugangsschlüssel erzeugen (15–20 Min.)**
1. Den [Graph API Explorer](https://developers.facebook.com/tools/explorer/) öffnen.
2. Rechts bei **Meta App** die App `GfbV Linkseite` auswählen.
3. Bei **Nutzer oder Seite** → **Nutzer-Zugriffsschlüssel abrufen**.
4. Unter **Berechtigungen** diese hinzufügen:
   `pages_show_list`, `pages_read_engagement`, `instagram_basic`
   (falls die Seite in einem Business-Portfolio liegt, zusätzlich `business_management`).
5. **Generate Access Token** klicken. Im Anmeldefenster die **Facebook-Seite der GfbV** und das **Instagram-Konto** auswählen und bestätigen.
6. Den erzeugten Schlüssel kopieren. Er gilt nur eine Stunde, deshalb jetzt verlängern:
   [Zugriffsschlüssel-Debugger](https://developers.facebook.com/tools/debug/accesstoken/) öffnen, Schlüssel einfügen, **Debug**, dann unten **Zugriffsschlüssel verlängern**. Den neuen, langen Schlüssel kopieren.
7. Zurück im Graph API Explorer: den langen Schlüssel oben ins Feld **Zugriffsschlüssel** einfügen. In die Abfragezeile eintragen:
   ```
   me/accounts?fields=name,access_token,instagram_business_account
   ```
   und **Absenden**.
8. In der Antwort steht bei der GfbV-Seite:
   - `access_token` → das ist der **Seiten-Schlüssel** (eine lange Zeichenkette)
   - `instagram_business_account` → `id` → das ist die **Instagram-ID** (eine lange Zahl)
9. Zur Kontrolle den Seiten-Schlüssel im Zugriffsschlüssel-Debugger prüfen: Bei **Läuft ab** muss **Nie** stehen.

Den Schlüssel nirgends speichern oder per E-Mail verschicken. Er gehört nur in GitHub (Schritt 9).

**Schritt 9 · Schlüssel bei GitHub hinterlegen (5 Min.)**
1. Im Projekt: **Settings** → links **Secrets and variables** → **Actions** → **New repository secret**.
2. Name `IG_TOKEN`, Wert: der Seiten-Schlüssel. **Add secret**.
3. Noch einmal **New repository secret**: Name `IG_USER_ID`, Wert: die Instagram-ID. **Add secret**.

**Schritt 10 · Ersten Lauf starten und prüfen (10 Min.)**
1. **Actions** → links **Beiträge aktualisieren** → rechts **Run workflow** → **Run workflow**.
2. Nach etwa einer Minute den Lauf öffnen. Beim Schritt „Neue Instagram-Beiträge abrufen“ steht z. B.:
   *„30 Beiträge von Instagram abgerufen. … Fertig: 24 Beiträge auf der Seite, 13 neu …“*
3. Die Seite neu laden. Ältere Posts ohne Link in der Caption führen auf den Ersatzlink gfbv.de/aktuelles/news/ und tragen die Art „Aktuelles“. Wichtige davon lassen sich über `korrekturen.json` nachbessern (siehe unten).

**Schritt 11 · Team informieren (10 Min.)**
Zwei Regeln für jede Caption, siehe „Regeln fürs Posten“ unten.

---

### Phase 3 – GfbV-Adresse (ca. 15 Min. plus Wartezeit)

**Schritt 12 · DNS-Eintrag (IT, 15 Min.)**
Die IT legt bei der Domainverwaltung von gfbv.de einen Eintrag an:

| Typ | Name | Ziel |
|---|---|---|
| CNAME | `instagram` | `gfbv-ev.github.io` (Name der Organisation aus Schritt 2 + `.github.io`) |

**Schritt 13 · Adresse bei GitHub eintragen (5 Min.)**
1. **Settings** → **Pages** → **Custom domain**: `instagram.gfbv.de` → **Save**.
2. GitHub prüft den DNS-Eintrag. Danach Häkchen bei **Enforce HTTPS** setzen, sobald es anwählbar ist. Das dauert meist unter einer Stunde, selten bis zu einem Tag.

**Schritt 14 · Link in die Instagram-Bio (2 Min.)**
`instagram.gfbv.de` als Link im Profil von @bedrohtevoelker eintragen.

---

## Regeln fürs Posten

Damit jede Kachel gut aussieht und richtig verlinkt:

1. **Die erste Zeile der Caption ist die Überschrift.** Sie wird zum Kacheltitel (Emojis werden entfernt, nach 70 Zeichen gekürzt). Kurz und klar formulieren.
2. **Der Ziel-Link steht in der Caption**, am besten am Ende, z. B.
   `Mehr: gfbv.de/aktuelles/news/…`
   Die Kachel führt dann direkt dorthin. Fehlt der Link, führt sie auf gfbv.de/aktuelles/news/.

Aus dem Link ergibt sich die Art der Kachel automatisch: Artikel, Zeitschrift, Termin, Publikation, Petition, Stelle, Spenden, Region, Thema.

---

## Im Alltag

**Titel oder Link eines Beitrags korrigieren**
1. Im Projekt die Datei `skript/korrekturen.json` öffnen → Stift-Symbol (bearbeiten).
2. Einen Eintrag ergänzen. Das Kürzel steht in der Post-Adresse: instagram.com/p/**DeRPpLdDe6O**/
   ```json
   "DeRPpLdDe6O": { "titel": "Kürzerer Titel", "ziel": "https://www.gfbv.de/…" },
   ```
   Auf Kommas zwischen den Einträgen achten.
3. **Commit changes**. Die Seite ist nach ca. einer Minute aktualisiert.

**Einen Beitrag ausblenden**
In `korrekturen.json`: `"KÜRZEL": { "ausblenden": true },`

**Einen Beitrag von Hand ergänzen** (z. B. Kooperationspost eines anderen Accounts)
1. Bild (erstes Slide, 4:5) unter `site/bilder/` hochladen, Dateiname = Kürzel, z. B. `ABC123.jpg`.
2. In `skript/manuell.json` einen Eintrag nach dem Muster des vorhandenen ergänzen.

**Wenn etwas nicht läuft**
- Schlägt ein Lauf fehl, schickt GitHub eine E-Mail an die Admins der Organisation. Die Seite bleibt dann auf dem letzten Stand und geht nicht kaputt.
- Meldung *„Zugangsschlüssel ungültig“*: Das passiert, wenn das Facebook-Passwort geändert oder Admin-Rechte entzogen wurden. Schritt 8 und 9 wiederholen.
- Nach 60 Tagen ohne neuen Post pausiert GitHub den Zeitplan. Unter **Actions** erscheint dann ein Hinweis mit dem Knopf **Enable workflow**.
- Meta schaltet alte Schnittstellen-Versionen nach etwa zwei Jahren ab. In `skript/einstellungen.json` steht die Version (`api_version`). Wenn ein Lauf mit einem Versionshinweis scheitert, dort die aktuelle Version eintragen.

---

## Rechtliches

- **Schrift:** Aller, Dalton Maag, Standard Edition. Lizenztexte in `site/schrift/`. Die kostenlose Lizenz deckt bis zu 25 Nutzer*innen bzw. 25.000 Website-Besucher*innen pro Tag.
- **Datenschutz:** Die Seite setzt keine Cookies, lädt keine externen Schriften und nutzt kein Tracking. GitHub (Microsoft) speichert beim Ausliefern technische Server-Logs (u. a. IP-Adressen). Das sollte einen Satz in der Datenschutzerklärung von gfbv.de bekommen.
