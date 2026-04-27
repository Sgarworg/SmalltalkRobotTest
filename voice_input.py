import sounddevice as sd
import soundfile as sf
import numpy as np
from config import config
from faster_whisper import WhisperModel


model = WhisperModel(config["whisper_model"], device="cpu", compute_type="int8")

def record_until_silence(samplerate=16000, silence_threshold = config["silence_threshold"], silence_duration=config["silence_duration"]):
    print("Sprich jetzt...")

    chunks = []
    silent_chunks = 0
    chunks_per_second = 10  # wie oft pro Sekunde gemessen wird
    chunk_size = samplerate // chunks_per_second
    silence_limit = int(silence_duration * chunks_per_second)

    with sd.InputStream(samplerate=samplerate, channels=1, dtype='float32') as stream:
        first_word = False
        while True:
            chunk, _ = stream.read(chunk_size)
            chunks.append(chunk.copy())

            volume = np.abs(chunk).mean()

            if volume >= silence_threshold:
                first_word = True
                silent_chunks = 0

            if volume < silence_threshold and first_word:
                silent_chunks += 1

            if first_word:
                filled = int((silent_chunks / silence_limit) * 20)
                bar =  "█" * (20 - filled) + "░" * filled
                print(f"\r Stille: [{bar}] {silence_limit -silent_chunks }/{silence_limit}", end="", flush=True)
            else:
                print(f"\r Warte auf Sprache...", end="", flush=True)

            if silent_chunks >= silence_limit and first_word:
                break

    print("\nFertig")
    audio = np.concatenate(chunks)
    sf.write("temp.wav", audio, samplerate)

def record_audio(seconds=5, samplerate=16000):
    print("Aufnahme läuft...")
    audio = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()
    print("Fertig")
    sf.write("temp.wav", audio, samplerate)

def transcribe():
    record_until_silence()
    segments, _ = model.transcribe("temp.wav", language="de")
    text = " ".join([s.text for s in segments])
    return text.strip()