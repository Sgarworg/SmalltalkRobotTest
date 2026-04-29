# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projekt

Bachelor-Thesis: **LLM-gestützte Roboter-Interaktion in Pflegeeinrichtungen.**
Ziel ist ein vollständig lokaler, deutschsprachiger Voice Assistant auf einem Roboter (Baujahr 2016), der soziale Isolation von Bewohnern in Pflegeheimen reduziert. Latenz ist kritisch — Gespräche müssen natürlich wirken.

Lies immer **`DECISIONS.md`** bevor du Architektur- oder Modell-Entscheidungen triffst oder vorschlägst. Dort sind alle bisherigen Entscheidungen mit Begründung dokumentiert. Neue Entscheidungen dort nachtragen.

Lies **`cloud.md`** für Benchmark-Ergebnisse der getesteten LLM-Modelle (Latenz, tok/s, Tool Calling).

## Stack

- **Python 3.13** (venv unter `venv/`)
- **LLM:** Ollama `AsyncClient` → Qwen3 auf NVIDIA Spark. Modell per `config.json → ollama_model` umschaltbar.
- **STT:** `faster-whisper` (Modell `small`, CPU, int8) — aufnehmen bis Stille erkannt, dann transkribieren
- **TTS:** Piper TTS (`de_DE-thorsten-high.onnx`) — vorerst wegen Python 3.13. XTTS v2 geplant nach Python-Downgrade auf 3.11.
- **DB:** TinyDB (`database.json`) für Rezepte
- **Tools:** Plain async Funktionen in `tools.py`, Ollama-Schemas in `TOOLS`, Dispatch via `TOOL_MAP`

## Starten

```bash
source venv/bin/activate
python main.py
```

Voraussetzung: Ollama läuft auf dem NVIDIA Spark und das konfigurierte Modell ist gepullt.

## Benchmarks ausführen

```bash
python benchmark.py   # schreibt Ergebnisse in cloud.md
```

Modelle in `benchmark.py → MODELS` anpassen (nur bereits gepullte Modelle eintragen).

## Architektur

```
main.py          — Hauptschleife: STT → Ollama Tool-Calling Loop → TTS
tools.py         — Tool-Funktionen (async) + TOOLS (Schemas) + TOOL_MAP (Dispatch)
voice_input.py   — Aufnahme (sounddevice) + Transkription (faster-whisper)
voice_output.py  — Piper TTS → sounddevice
config.py        — lädt config.json
database.py      — TinyDB-Instanz für Rezepte
benchmark.py     — Modell-Benchmarks, schreibt cloud.md
```

### Tool-Calling Loop (`main.py`)

Ollama antwortet entweder mit Tool-Calls oder Text. Bei Tool-Calls: Tool ausführen, Ergebnis als `role: tool` in die Message-History, erneut an Ollama schicken — bis keine Tool-Calls mehr kommen, dann TTS.

### Neues Tool hinzufügen

1. Async-Funktion in `tools.py` schreiben (gibt `str` zurück)
2. In `TOOL_MAP` eintragen
3. Ollama-Schema in `TOOLS` eintragen

## Konfiguration (`config.json`)

| Key | Bedeutung |
|---|---|
| `ollama_model` | Ollama-Modellname (z.B. `qwen3:8b`) |
| `piper_model` | Dateiname des Piper `.onnx`-Modells |
| `whisper_model` | faster-whisper Modellgröße (`small`, `medium`, …) |
| `silence_duration` | Sekunden Stille bis Aufnahme stoppt |
| `silence_threshold` | Lautstärke-Schwelle für Stille-Erkennung |
| `system_prompt` | System-Prompt für das LLM |

## Wichtige Constraints

- **Kein Cloud-API-Betrieb** — Pflegedaten dürfen das Haus nicht verlassen (Datenschutz)
- **TTS-Ausgabe muss TTS-kompatibel sein** — kein Markdown, keine Sonderzeichen außer Umlauten; das steht im System-Prompt
- **Piper-Modell-Dateien** (`.onnx`, `.onnx.json`) sind per `.gitignore` ausgeschlossen — müssen manuell heruntergeladen werden (siehe `DECISIONS.md`)