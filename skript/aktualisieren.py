#!/usr/bin/env python3
"""
Aktualisiert die Link-in-Bio-Seite der GfbV aus Instagram.

Ablauf bei jedem Lauf:
  1. Neueste Beiträge über die Instagram-Schnittstelle von Meta abrufen.
  2. Pro Beitrag das Titelbild speichern (erstes Slide, bei Reels das Vorschaubild).
  3. Titel (erste Zeile der Caption), Ziel-Link (gfbv.de-Adresse aus der Caption)
     und Art (aus dem Link abgeleitet) ermitteln.
  4. Korrekturen (skript/korrekturen.json) und manuelle Beiträge (skript/manuell.json)
     anwenden.
  5. site/beitraege.json schreiben und nicht mehr benötigte Bilder löschen.

Benötigt nur Python 3.9+ ohne Zusatzpakete.

Umgebungsvariablen (als GitHub-Secrets hinterlegt):
  IG_TOKEN    Seiten-Zugangsschlüssel von Meta (läuft nicht ab)
  IG_USER_ID  ID des Instagram-Business-Kontos

Fehlt IG_TOKEN, wird der Abruf übersprungen; Korrekturen werden trotzdem angewendet.

Zum Testen ohne Schnittstelle:  python3 skript/aktualisieren.py --testdaten datei.json
"""

import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    BERLIN = ZoneInfo("Europe/Berlin")
except Exception:  # pragma: no cover
    BERLIN = None

WURZEL = Path(__file__).resolve().parent.parent
SITE = WURZEL / "site"
BILDER = SITE / "bilder"
DATEN = SITE / "beitraege.json"
SKRIPT = WURZEL / "skript"


def lade_json(pfad, standard):
    try:
        with open(pfad, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return standard
    except json.JSONDecodeError as e:
        print(f"FEHLER in {Path(pfad).name}, Zeile {e.lineno}: {e.msg}.")
        print("→ Meist fehlt ein Komma zwischen zwei Einträgen oder ein Anführungszeichen.")
        sys.exit(1)


EINSTELLUNGEN = {
    "anzahl_auf_der_seite": 24,
    "abruf_anzahl": 30,
    "titel_max_zeichen": 70,
    "ersatz_link": "https://www.gfbv.de/aktuelles/news/",
    "api_version": "v23.0",
    **lade_json(SKRIPT / "einstellungen.json", {}),
}

# Art des Beitrags, abgeleitet aus dem Link (erste passende Regel gilt)
ARTEN = [
    ("gfbv.de/aktuelles/news/", "Artikel"),
    ("gfbv.de/aktuelles/zeitschrift", "Zeitschrift"),
    ("gfbv.de/aktuelles/termine", "Termin"),
    ("gfbv.de/aktuelles/publikationen", "Publikation"),
    ("gfbv.de/publikation/", "Publikation"),
    ("gfbv.de/mitmachen/petition", "Petition"),
    ("gfbv.de/mitmachen/aktuelle-stellen", "Stelle"),
    ("gfbv.de/mitmachen/jobs", "Stelle"),
    ("gfbv.de/mitmachen/", "Mitmachen"),
    ("gfbv.de/spenden", "Spenden"),
    ("gfbv.de/region/", "Region"),
    ("gfbv.de/voelker/", "Hintergrund"),
    ("gfbv.de/thema/", "Thema"),
    ("gfbv.de/newsletter", "Newsletter"),
    ("gfbv.de", "Beitrag"),
]

GFBV_LINK = re.compile(r"(?:https?://)?(?:www\.)?gfbv\.de(/[^\s)\]»«\"“”‘’<>]*)?", re.I)
ANDERER_LINK = re.compile(r"https?://[^\s)\]»«\"“”‘’<>]+", re.I)
KUERZEL = re.compile(r"instagram\.com/(?:[^/]+/)?(p|reel|tv)/([A-Za-z0-9_-]+)")
# Zeichen, die wie Emojis wirken, aber nicht als Symbol eingestuft sind
EMOJI_EXTRA = set("‼⁉ℹⓂ〰〽㊗㊙‍︎️⃣")


# ── Text ──────────────────────────────────────────────────────────

def saeubern(text):
    text = GFBV_LINK.sub(" ", text)
    text = ANDERER_LINK.sub(" ", text)
    text = re.sub(r"[#@](?=\w)", "", text)  # #Damaskus → Damaskus, @bundesregierung → bundesregierung
    text = "".join(
        c for c in text
        if c not in EMOJI_EXTRA and unicodedata.category(c) not in ("So", "Sk", "Cs", "Co", "Cn")
        and not (0x1F1E6 <= ord(c) <= 0x1F1FF)  # Flaggen-Buchstaben
    )
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -–—:|·•.,;")


def kuerzen(text, maximal):
    if len(text) <= maximal:
        return text
    schnitt = text[: maximal + 1]
    leer = schnitt.rfind(" ")
    if leer > maximal * 0.6:
        schnitt = schnitt[:leer]
    else:
        schnitt = schnitt[:maximal]
    return schnitt.rstrip(" ,;:–-") + "…"


def titel_aus(caption):
    for zeile in (caption or "").splitlines():
        t = saeubern(zeile)
        # Zeilen wie „Mehr: gfbv.de/…“ oder reine Emoji-Zeilen überspringen
        if len(re.sub(r"[^\w]", "", t)) >= 8 and not re.fullmatch(r"(?i)(mehr|link|infos?)( in der bio)?", t):
            return kuerzen(t, EINSTELLUNGEN["titel_max_zeichen"])
    return "Neuer Beitrag"


def link_aus(caption):
    caption = caption or ""
    treffer = [m for m in GFBV_LINK.finditer(caption) if m.group(1) and len(m.group(1)) > 1]
    if treffer:
        pfad = treffer[-1].group(1).rstrip(".,;:!?)…")
        return "https://www.gfbv.de" + pfad
    andere = ANDERER_LINK.findall(caption)
    if andere:
        return andere[-1].rstrip(".,;:!?)…")
    return EINSTELLUNGEN["ersatz_link"]


def art_aus(link):
    l = link.lower()
    for muster, art in ARTEN:
        if muster in l:
            return art
    return "Link"


def datum_aus(zeitstempel):
    # Meta liefert z. B. 2026-10-09T08:15:02+0000
    try:
        d = datetime.strptime(zeitstempel, "%Y-%m-%dT%H:%M:%S%z")
        if BERLIN:
            d = d.astimezone(BERLIN)
        return d.strftime("%Y-%m-%d")
    except Exception:
        return (zeitstempel or "")[:10]


# ── Schnittstelle ─────────────────────────────────────────────────

def abrufen(url):
    anfrage = urllib.request.Request(url, headers={"User-Agent": "gfbv-linkseite"})
    with urllib.request.urlopen(anfrage, timeout=30) as antwort:
        return antwort.read()


def instagram_beitraege(token, nutzer_id):
    felder = "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,children{media_type,media_url,thumbnail_url}"
    parameter = urllib.parse.urlencode({
        "fields": felder,
        "limit": EINSTELLUNGEN["abruf_anzahl"],
        "access_token": token,
    })
    url = f"https://graph.facebook.com/{EINSTELLUNGEN['api_version']}/{nutzer_id}/media?{parameter}"
    try:
        daten = json.loads(abrufen(url))
    except urllib.error.HTTPError as e:
        try:
            meldung = json.loads(e.read()).get("error", {}).get("message", "")
        except Exception:
            meldung = ""
        meldung = meldung.replace(token, "***")
        print(f"FEHLER: Instagram-Schnittstelle antwortet mit {e.code}. {meldung}")
        if e.code in (400, 401, 403):
            print("→ Meist ist der Zugangsschlüssel ungültig geworden (Passwort geändert, Rechte entzogen).")
            print("  Neuen Schlüssel erzeugen, siehe Anleitung, Schritt 8.")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"FEHLER: Instagram nicht erreichbar ({e.reason}). Nächster Versuch beim nächsten Lauf.")
        sys.exit(1)
    return daten.get("data", [])


def bild_url(medium):
    typ = medium.get("media_type")
    if typ == "CAROUSEL_ALBUM":
        kinder = (medium.get("children") or {}).get("data") or []
        if kinder:
            erstes = kinder[0]
            return erstes.get("media_url") if erstes.get("media_type") == "IMAGE" else erstes.get("thumbnail_url")
        return medium.get("media_url")
    if typ == "VIDEO":
        return medium.get("thumbnail_url")
    return medium.get("media_url")


def bild_speichern(url, kuerzel):
    ziel = BILDER / f"{kuerzel}.jpg"
    if ziel.exists():
        return f"bilder/{kuerzel}.jpg"
    if not url:
        return None
    try:
        inhalt = abrufen(url)
    except Exception as e:
        print(f"  Bild für {kuerzel} nicht ladbar ({e}), Beitrag wird beim nächsten Lauf erneut versucht.")
        return None
    BILDER.mkdir(parents=True, exist_ok=True)
    ziel.write_bytes(inhalt)
    return f"bilder/{kuerzel}.jpg"


def eintrag_aus(medium):
    m = KUERZEL.search(medium.get("permalink") or "")
    if not m:
        return None
    kuerzel = m.group(2)
    bild = bild_speichern(bild_url(medium), kuerzel)
    if not bild:
        return None
    caption = medium.get("caption") or ""
    ziel = link_aus(caption)
    return {
        "kuerzel": kuerzel,
        "datum": datum_aus(medium.get("timestamp", "")),
        "art": "Aktuelles" if ziel == EINSTELLUNGEN["ersatz_link"] else art_aus(ziel),
        "titel": titel_aus(caption),
        "ziel": ziel,
        "bild": bild,
        "instagram": medium.get("permalink"),
        "_zeit": medium.get("timestamp", ""),
    }


# ── Hauptablauf ───────────────────────────────────────────────────

def main():
    vorhanden = {b["kuerzel"]: b for b in lade_json(DATEN, []) if b.get("kuerzel")}
    korrekturen = {k: v for k, v in lade_json(SKRIPT / "korrekturen.json", {}).items() if not k.startswith("_")}
    manuell = lade_json(SKRIPT / "manuell.json", {}).get("beitraege", [])

    medien = None
    if "--testdaten" in sys.argv:
        datei = sys.argv[sys.argv.index("--testdaten") + 1]
        medien = lade_json(datei, {}).get("data", [])
        print(f"Testmodus: {len(medien)} Beiträge aus {datei}")
    else:
        token = os.environ.get("IG_TOKEN", "").strip()
        nutzer_id = os.environ.get("IG_USER_ID", "").strip()
        if not token:
            print("Kein Instagram-Zugangsschlüssel hinterlegt (IG_TOKEN). Abruf übersprungen.")
        elif not nutzer_id:
            print("FEHLER: IG_USER_ID fehlt. Siehe Anleitung, Schritt 8.")
            sys.exit(1)
        else:
            medien = instagram_beitraege(token, nutzer_id)
            print(f"{len(medien)} Beiträge von Instagram abgerufen.")

    neu = 0
    for medium in medien or []:
        e = eintrag_aus(medium)
        if not e:
            continue
        if e["kuerzel"] not in vorhanden:
            neu += 1
            print(f"  Neu: {e['datum']} · {e['titel']} → {e['ziel']}")
        vorhanden[e["kuerzel"]] = e

    for e in manuell:
        if e.get("kuerzel"):
            vorhanden[e["kuerzel"]] = {**vorhanden.get(e["kuerzel"], {}), **e}

    liste = []
    for kuerzel, e in vorhanden.items():
        k = korrekturen.get(kuerzel, {})
        if k.get("ausblenden"):
            continue
        e = {**e, **{f: k[f] for f in ("titel", "ziel", "art", "datum") if k.get(f)}}
        if k.get("ziel") and not k.get("art"):
            e["art"] = art_aus(k["ziel"])
        liste.append(e)

    liste.sort(key=lambda e: (e.get("datum", ""), e.get("_zeit", "")), reverse=True)
    liste = liste[: EINSTELLUNGEN["anzahl_auf_der_seite"]]
    for e in liste:
        e.pop("_zeit", None)

    # Bilder entfernen, die auf der Seite nicht mehr vorkommen
    genutzt = {Path(e["bild"]).name for e in liste if e.get("bild")}
    entfernt = 0
    for datei in BILDER.glob("*"):
        if datei.is_file() and datei.name not in genutzt and not datei.name.startswith("."):
            datei.unlink()
            entfernt += 1

    neu_json = json.dumps(liste, ensure_ascii=False, indent=2) + "\n"
    alt_json = DATEN.read_text(encoding="utf-8") if DATEN.exists() else ""
    if neu_json != alt_json:
        DATEN.write_text(neu_json, encoding="utf-8")
    print(f"Fertig: {len(liste)} Beiträge auf der Seite, {neu} neu, {entfernt} alte Bilder entfernt.")


if __name__ == "__main__":
    main()
