# Stromverbrauch Schweiz 1990–2025

Visualisierungsprojekt VDSS (FS26 — Gruppe 4)

Dieses Projekt untersucht die Entwicklung des Schweizer Stromverbrauchs zwischen
1990 und 2025 und macht saisonale Muster und langfristige Trends sichtbar. Im
Mittelpunkt steht die Frage, ob die Schweiz trotz Bevölkerungswachstum und
wärmerer Winter wirklich effizienter geworden ist — beantwortet anhand
öffentlich verfügbarer Daten von BFE, BFS und MeteoSchweiz.

**Team:** Silvan, Salomon, Fabian

## Projektorganisation

Die Entwicklung folgt dem Prozessmodell für Visualisierungsprodukte aus dem
Modul. Code und Konfigurationen liegen in den Phasenordnern, die Dokumentation
als Quarto-Projekt in `docs/`.

![Prozessmodell](docs/pics/vizproductprocess.png)

| Phase                            | Code-Ordner            | Dokumentation                |
|----------------------------------|------------------------|------------------------------|
| Projektverständnis               | —                      | `docs/project_charta.qmd`    |
| Datenakquise & Aufbereitung      | `data_acquisition/`    | `docs/data_report.qmd`       |
| Explorative Datenanalyse         | `eda/`                 | `docs/data_report.qmd`       |
| Visual Design                    | `viz_design/`          | `docs/viz_design_report.qmd` |
| Implementierung (Dashboard)      | `Dashboard/`           | `docs/viz_design_report.qmd` |
| Evaluation                       | `evaluation/`          | `docs/viz_design_report.qmd` |
| Deployment                       | `deployment/` + `.github/workflows/` | `docs/deployment.qmd` |

Die Heizbedarf-Werte für die Jahre 1990–1993 stammen aus einer eigenen
Regression (`data_acquisition/regression_heizbedarf.py`), da MeteoSchweiz für
diesen Zeitraum keine direkten Werte publiziert.

📖 **Live-Dokumentation:** <https://vdss-fs26-ds25a.github.io/Visualisation-Projekt-Gruppe-4/>
*(automatisch deployed via GitHub Actions bei jedem Push auf `main`)*

## Dashboard ausführen

Das interaktive Dashboard liegt in `Dashboard/` und ist mit
[Streamlit](https://streamlit.io/) gebaut.

### Schnellstart (Windows)

Doppelklick auf `Dashboard/start_Dashboard_Industrie_Reaktor.bat`.

Das Skript erstellt beim ersten Start ein virtuelles Environment (`venv/`),
installiert die Requirements und startet Streamlit. Beim nächsten Mal überspringt
es Setup und Installation und öffnet das Dashboard direkt im Browser unter
<http://localhost:8501>.

### Manuell

```bash
cd Dashboard
python -m venv venv
venv\Scripts\activate           # Windows
# source venv/bin/activate      # macOS / Linux
pip install -r requirements.txt
streamlit run Dashboard_Industrie_Reaktor.py
```

### Module im Dashboard

| Modul                    | Inhalt                                                                        |
|--------------------------|-------------------------------------------------------------------------------|
| Übersicht                | Stromverbrauch im Zeitverlauf mit 3/6/9/12-Monats-Trend und Bevölkerung       |
| Verbrauch × Temperatur   | Doppelachsen-Vergleich Jahresmittel-Verbrauch und -Temperatur                 |
| Korrelation              | Streudiagramm Temperatur vs. Verbrauch pro Kopf, Vergleich Wachstum/Sättigung |
| Effizienz / Heizen       | Witterungsbereinigte Effizienz (Verbrauch ÷ Heizbedarf) über die Zeit         |

Filterbar nach Zeitbereich und Jahreszeiten; oben rechts die Kernkraft-Kennzahl
und in der Sidebar der Reaktor-Auslastungs-Indikator je nach selektierten Saisons.

## Python-Environment für Analyse & Dokumentation

Für die Analyse-Skripte (`eda/`, `data_acquisition/`) und das Rendern der
Quarto-Doku wird ein eigenes Python-Environment mit
[`uv`](https://docs.astral.sh/uv/) verwaltet (siehe `pyproject.toml` und
`uv.lock`). Das Dashboard hat ein separates Environment — siehe Abschnitt
*Dashboard ausführen*.

### Setup (einmalig)

[uv installieren](https://docs.astral.sh/uv/getting-started/installation/), dann
im Projekt-Root:

```bash
uv sync
```

Erstellt `.venv/` mit allen Abhängigkeiten aus `pyproject.toml` und der gepinnten
Version in `uv.lock`.

### Verwendung

Jeden Python-Befehl mit `uv run` ausführen:

```bash
uv run python eda/generate-data-profile.py
uv run quarto render
```

Oder das Environment direkt aktivieren (Linux/macOS):

```bash
source .venv/bin/activate
```

### Pakete verwalten

```bash
uv add <package>       # neues Paket hinzufügen
uv remove <package>    # Paket entfernen
```

`pyproject.toml` und `uv.lock` immer committen, damit das Team denselben Stand hat.

## Dokumentation (Quarto)

Die Projektdokumentation liegt als Quarto-Projekt in `docs/`. Die einzelnen
`.qmd`-Dateien (Project Charta, Data Report, Viz-Design-Report, Deployment)
ergeben gemeinsam die Doku-Webseite.

Online: <https://vdss-fs26-ds25a.github.io/Visualisation-Projekt-Gruppe-4/>

### Lokal arbeiten

Voraussetzung: [Quarto installieren](https://quarto.org/docs/get-started/)
(einmalig), Python-Env vorhanden (`uv sync`).

```bash
cd docs
uv run quarto preview          # Live-Vorschau mit Auto-Reload
uv run quarto render           # Statischen Build nach docs/build/ schreiben
```

Der `uv run`-Vorsatz stellt sicher, dass Python-Code-Chunks in den `.qmd`-Files
das Projekt-Environment finden.

### Deployment

Jeder Push auf `main` löst den GitHub-Actions-Workflow `.github/workflows/publish.yml`
aus, der die Quarto-Doku rendert und auf GitHub Pages deployt. Die berechneten
Python-Resultate werden aus `docs/_freeze/` geladen (per `execute: freeze: auto`
in `_quarto.yml`), sodass der Workflow ohne lokales Python auskommt.
