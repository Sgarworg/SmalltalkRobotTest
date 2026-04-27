import sounddevice as sd
import numpy as np
from elevenlabs.client import AsyncElevenLabs
from elevenlabs import VoiceSettings
from config import config
from dotenv import load_dotenv
import subprocess
import pyttsx3
import os
import io

load_dotenv()

async def speak(text):
    client = AsyncElevenLabs(api_key=os.environ.get("ELEVENLABS_API_KEY"))

    audio_data = b""
    async for chunk in client.text_to_speech.convert(
        voice_id=config["voice_id"],
        model_id=config["tts_model"],
        text=text,

        voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75),
    ):
        audio_data += chunk

    # MP3 via ffmpeg zu PCM konvertieren
    process = subprocess.run(
        ["ffmpeg", "-i", "pipe:0", "-f", "s16le", "-ar", "44100", "-ac", "1", "pipe:1"],
        input=audio_data,
        capture_output=True
    )
    samples = np.frombuffer(process.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    sd.play(samples, samplerate=44100)
    sd.wait()

def cheap_speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[5].id)  # Anna - Deutsch
    engine.setProperty('rate', 180)
    engine.say(text)
    engine.runAndWait()