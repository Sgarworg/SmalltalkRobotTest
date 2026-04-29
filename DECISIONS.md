# Entscheidungen & Modelle

## Projektziel

Sprachassistent für einen Roboter — vollständig lokal, kein Cloud-API-Geld.
Der Nutzer spricht mit dem Roboter, der versteht, denkt nach und antwortet per Sprache.

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

**Getestet & verworfen:** `qwen:latest` — kein Tool-Calling-Support.
**Aktuell:** `qwen3:8b` — unterstützt Tool Calling, schnell, läuft lokal auf dem Spark.

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

## Sprachmodell: Ollama + Qwen3 (lokal auf NVIDIA Spark)

**Library:** `ollama` Python-Client (`AsyncClient`)
**Inference-Server:** Ollama (Entwicklung), vLLM (Produktion auf dem Spark)
**Aktuelles Modell:** `qwen3:8b`
Modell konfigurierbar per `ollama_model` in `config.json`.

Ablösung von `claude_agent_sdk` + Anthropic API — vollständig lokal, keine API-Kosten, Datenschutz gewährleistet (Pflegedaten bleiben lokal).

### Modellwahl: Zwei-Modell-Strategie

| Modell | Stärke | Einsatz |
|---|---|---|
| **Qwen3-8B** | Sehr schnell, gutes Deutsch, Tool Calling | Default: Small Talk, Speiseplan, HAW-Infos |
| **Qwen3-32B** | Besser bei Emotion & Nuance, langsamer | Erzählmodus, emotionale Gespräche, Demenz-Anwendungsfall |

Gemma 3 27B wurde geprüft und verworfen: kein natives Tool Calling.

Modell per `config.json` umschaltbar — ermöglicht empirischen Vergleich (Latenz vs. wahrgenommene Natürlichkeit) als Teil der Thesis-Evaluation.

**Modell-Auswahl:**
- `qwen:latest` → verworfen, kein Tool-Calling-Support
- `qwen3:32b` → Tool Calling ✅, aber langsam (20 GB)
- `qwen3:8b` → Tool Calling ✅, deutlich schneller, aktuell im Einsatz

---

## Tool-Integration: Ollama Tool Calling (nativ)

Tools als plain async Python-Funktionen, Ollama-Schemas als Liste in `TOOLS`.
Dispatch über `TOOL_MAP` (Name → Funktion) in `tools.py`.
Ablösung von MCP — einfacher, kein separater Server-Prozess.

---

## Debug-Modus: Texteingabe statt Mikrofon

`DEBUG_MODE = True` in `voice_input.py` ersetzt die Mikrofon-Aufnahme durch einfache Texteingabe (`input()`).
Hintergrund: Entwicklung läuft remote über Windows-App auf dem NVIDIA Spark — kein Mikrofon-Zugriff möglich.
Zum Aktivieren des echten Sprachmodus: `DEBUG_MODE = False` setzen.

---

## Datenbank: TinyDB

Für Rezepte. JSON-Datei (`database.json`), kein separater DB-Server nötig.
Passt für kleine lokale Datenmenge.