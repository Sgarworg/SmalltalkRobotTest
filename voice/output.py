import numpy as np
import sounddevice as sd
from TTS.api import TTS
from core.config import config

_XTTS_SAMPLE_RATE = 24000

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")


def speak(text: str):
    wav = tts.tts(
        text=text,
        speaker=config.get("xtts_speaker", "Claribel Dervla"),
        language="de",
    )
    sd.play(np.array(wav, dtype=np.float32), samplerate=_XTTS_SAMPLE_RATE)
    sd.wait()
