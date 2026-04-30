"""
TTS Stimmen-Test: generiert Audiodateien für verschiedene Sprecher/Modelle und lädt sie hoch.

Verwendung:
  python benchmark/tts_test.py                                    # alle XTTS-Stimmen
  python benchmark/tts_test.py --piper                            # Piper-Modell testen
  python benchmark/tts_test.py --speakers "Claribel Dervla" "Craig Gutsy"
  python benchmark/tts_test.py --text "Eigener Testtext"
  python benchmark/tts_test.py --list                             # alle Stimmen auflisten
"""

import argparse
import sys
import tempfile
from pathlib import Path

import numpy as np
import requests
import soundfile as sf

DEFAULT_TEXT = (
    "Guten Tag! Ich bin Ihr persönlicher Assistent hier im Pflegeheim. "
    "Wie geht es Ihnen heute? Kann ich Ihnen bei etwas helfen?"
)
XTTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
UPLOAD_URL = "https://tmpfiles.org/api/v1/upload"


def upload(path: Path) -> str:
    with open(path, "rb") as f:
        resp = requests.post(UPLOAD_URL, files={"file": (path.name, f)}, timeout=30)
    resp.raise_for_status()
    url = resp.json()["data"]["url"]
    return url.replace("tmpfiles.org/", "tmpfiles.org/dl/")


def test_xtts(speakers: list[str], text: str):
    from TTS.api import TTS
    print(f"\nModell: {XTTS_MODEL}")
    print(f"Text: \"{text}\"\n")
    print(f"{'Sprecher':<30} {'Status':<10} URL")
    print("-" * 90)

    tts = TTS(XTTS_MODEL)
    for speaker in speakers:
        try:
            wav = tts.tts(text=text, speaker=speaker, language="de", split_sentences=False)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = Path(tmp.name)
            sf.write(tmp_path, np.array(wav, dtype=np.float32), 24000)
            url = upload(tmp_path)
            tmp_path.unlink()
            print(f"{speaker:<30} {'OK':<10} {url}")
        except Exception as e:
            print(f"{speaker:<30} {'FEHLER':<10} {e}")


def test_piper(piper_model: str, text: str):
    from piper import PiperVoice
    print(f"\nModell: Piper ({piper_model})")
    print(f"Text: \"{text}\"\n")
    print(f"{'Sprecher':<30} {'Status':<10} URL")
    print("-" * 90)

    voice = PiperVoice.load(piper_model)
    chunks = list(voice.synthesize(text))
    audio = np.concatenate([c.audio_float_array for c in chunks])

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    sf.write(tmp_path, audio, chunks[0].sample_rate)
    url = upload(tmp_path)
    tmp_path.unlink()
    print(f"{'de_DE-thorsten-high':<30} {'OK':<10} {url}")


def main():
    parser = argparse.ArgumentParser(description="TTS Stimmen-Test")
    parser.add_argument("--text", default=DEFAULT_TEXT, help="Testtext")
    parser.add_argument("--speakers", nargs="+", help="Bestimmte XTTS-Sprecher testen")
    parser.add_argument("--piper", action="store_true", help="Piper-Modell testen")
    parser.add_argument("--piper-model", default="models/de_DE-thorsten-high.onnx")
    parser.add_argument("--list", action="store_true", help="Alle XTTS-Stimmen auflisten")
    args = parser.parse_args()

    if args.list:
        from TTS.api import TTS
        tts = TTS(XTTS_MODEL)
        print("\nVerfügbare Sprecher:")
        for s in tts.speakers:
            print(f"  {s}")
        sys.exit(0)

    if args.piper:
        test_piper(args.piper_model, args.text)

    if not args.piper or args.speakers:
        from TTS.api import TTS
        speakers = args.speakers or TTS(XTTS_MODEL).speakers
        test_xtts(speakers, args.text)


if __name__ == "__main__":
    main()
