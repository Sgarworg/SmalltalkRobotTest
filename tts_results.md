# TTS-Evaluierung: Sprachausgabe-Systeme

**Kontext:** Auswahl eines lokalen TTS-Systems für einen sozialen Roboter im Pflegekontext.
Anforderungen: natürliche Prosodie, gute Verständlichkeit, angemessene Tonalität für ältere Personen, vollständig lokal lauffähig (Datenschutz).

**Bewertungsskala:** 1 (ungenügend) bis 5 (sehr gut)

**Bewertete Dimensionen:** Natürlichkeit, Verständlichkeit, Deutsch-Qualität, Eignung für Pflegekontext

---

## 1. Piper TTS — `de_DE-thorsten-high`

| Kriterium | Bewertung |
|---|---|
| Gesamtwertung | 1 / 5 |
| Verständlichkeit | ungenügend |
| Natürlichkeit | sehr robotisch |

**Befund:** Ausgabe hakelig und stark rauschend. Ursache: Samplerate-Mismatch (22050 Hz Modell vs. 44100 Hz Ausgabegerät); Resampling brachte keine nennenswerte Verbesserung. Grundqualität des Modells unzureichend für den Pflegekontext.

**Entscheidung:** Verworfen.

---

## 2. Kokoro TTS

**Befund:** Kein Deutsch-Support (unterstützte Sprachen: EN, ES, FR, IT, JA, ZH).

**Entscheidung:** Verworfen — nicht evaluiert.

---

## 3. Coqui XTTS v2 — `tts_models/multilingual/multi-dataset/xtts_v2`

Multilinguales neuronales TTS-Modell mit Voice-Cloning-Unterstützung. Getestet wurden mehrere vortrainierte Sprecher-Embeddings auf deutschsprachigen Texten.



### Stimmen-Übersicht

| Stimme | Wertung | Charakteristik | Eignung |
|---|---|---|---|
| Claribel Dervla | 4 / 5 | neutral | bedingt geeignet — Artefakt-Problem |
| Daisy Studious | 2 / 5 | kindlich | nicht geeignet |
| Tammie Ema | 4 / 5 | streng, autoritär | bedingt geeignet — Tonalität zu hart |
| Asya Anara | 5 / 5 | beruhigend, warm | **Favorit** |
| Henriette Usha | 4 / 5 | freundlich | geeignet |
| Dionosio Schuyler | 3 / 5 | auffällige Betonung | bedingt geeignet |
| Abrahan Mack | 5 / 5 | freundlich, natürlich | **Favorit** |
| Nova Hogarth | 5 / 5 | sanft, gut verständlich | **Favorit** |

### Favoriten

- **Asya Anara** — beruhigende Wirkung, besonders geeignet für emotional belastete Situationen
- **Abrahan Mack** — freundliche, natürliche Prosodie
- **Nova Hogarth** — sanfte Stimme, hohe Verständlichkeit

---
