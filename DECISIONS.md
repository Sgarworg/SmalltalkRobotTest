# Entscheidungen & Modelle

## Ziel: Vollständig lokaler Betrieb (kein API-Geld)

Hardware: NVIDIA Spark (lokales GPU-System mit Ollama)

| Komponente | Aktuell | Ziel |
|---|---|---|
| STT | faster-whisper (local) ✅ | bleibt |
| LLM | Claude API (cloud) | Ollama + lokales Modell |
| TTS | pyttsx3 (local) / ElevenLabs (API) | lokales TTS-Modell |

---

### LLM: Ollama

Kandidat: `qwen:latest` (läuft bereits auf dem Spark)
Problem: `claude_agent_sdk` spricht die Anthropic API an — muss ersetzt oder umgebaut werden.
Optionen:
- Ollama direkt per HTTP (`/api/chat`) mit eigenem Tool-Calling-Loop
- OpenAI-kompatibler Endpoint von Ollama + passendes SDK

**Offen:** Tool-Calling-Support des gewählten Modells prüfen (nicht alle Ollama-Modelle können das zuverlässig).

---

### TTS: lokales Modell (offen)

pyttsx3 klingt schlecht. ElevenLabs fällt weg (API). Kandidaten für GPU-beschleunigte lokale TTS:
- **Kokoro** — sehr gute Qualität, schnell, läuft lokal
- **Piper** — leichtgewichtig, deutsche Stimmen verfügbar
- **Coqui XTTS v2** — hohe Qualität, braucht mehr VRAM

**Vorerst: Piper TTS** (`de_DE-thorsten-high`)
- Einzige Option die mit Python 3.13 läuft (Coqui XTTS v2 braucht <3.12)
- Kein GPU nötig, ONNX-basiert, sehr schnell
- Modell wird einmal beim Start geladen, Ausgabe direkt via `sounddevice`
- Modell-Datei: `de_DE-thorsten-high.onnx` (+ `.onnx.json`) im Projektordner

**Geplant: Coqui XTTS v2** sobald Python auf 3.11 gewechselt wird
- Deutlich natürlichere Stimme, Voice Cloning möglich
- Braucht GPU (8–16 GB VRAM) → gut für NVIDIA Spark

---

## Speech-to-Text: faster-whisper (small)

**Modell:** `small` (multilingual)
**Library:** `faster-whisper` mit `device="cpu"`, `compute_type="int8"`
**Sprache:** Deutsch (`language="de"` hart kodiert)

Lokales Modell, läuft ohne API-Kosten. `int8`-Quantisierung für schnellere CPU-Inferenz.
`small` als Kompromiss zwischen Genauigkeit und Geschwindigkeit.

---

## Text-to-Speech: pyttsx3 (Standard) / ElevenLabs (optional)

**Standard:** `pyttsx3` — lokal, kostenlos, Stimme: Index 5 (Anna, Deutsch), Rate: 180
**Premium:** ElevenLabs API — Modell `eleven_multilingual_v2`, Voice ID `JBFqnCBsd6RMkjVDRZzb`

Umschaltbar per `expensive_tts` in `config.json`.
ElevenLabs liefert deutlich natürlichere Sprache, kostet aber API-Credits.
Audio-Pipeline: ElevenLabs MP3 → ffmpeg → PCM → sounddevice.

---

## Sprachmodell: Ollama + qwen:latest (lokal)

**Library:** `ollama` Python-Client (`AsyncClient`)
**Modell:** `qwen:latest` auf NVIDIA Spark via Ollama
Modell konfigurierbar per `ollama_model` in `config.json`.

Ablösung von `claude_agent_sdk` + Anthropic API — vollständig lokal, keine API-Kosten.

---

## Tool-Integration: Ollama Tool Calling (nativ)

Tools als plain async Python-Funktionen, Ollama-Schemas als Liste in `TOOLS`.
Dispatch über `TOOL_MAP` (Name → Funktion) in `tools.py`.
Ablösung von MCP — einfacher, kein separater Server-Prozess.

---

## Datenbank: TinyDB

Für Rezepte. JSON-Datei (`database.json`), kein separater DB-Server nötig.
Passt für kleine lokale Datenmenge.