import numpy as np
import sounddevice as sd
from piper import PiperVoice
from config import config

tts_model = PiperVoice.load(config["piper_model"])


def speak(text: str):
    chunks = list(tts_model.synthesize(text))
    audio = np.concatenate([c.audio_float_array for c in chunks])
    sd.play(audio, samplerate=chunks[0].sample_rate)
    sd.wait()