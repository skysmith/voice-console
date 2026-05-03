#!/usr/bin/env python3
import os
from pynput import keyboard

from ptt import PushToTalkRecorder
from stt import transcribe_audio
from tts import speak
from ollama_client import OllamaChat


def load_env(path: str):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main():
    load_env("config.env")

    whisper_model = os.getenv("WHISPER_MODEL", "tiny.en")
    tts_voice = os.getenv("TTS_VOICE") or None

    chat = OllamaChat(
        model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        url=os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat"),
    )

    recorder = PushToTalkRecorder(sample_rate=16000)

    talking = False
    talk_key = keyboard.Key.space

    def on_press(key):
        nonlocal talking
        if key == talk_key and not talking:
            talking = True
            print("\n[talk] recording… (hold SPACE)")
            recorder.start()

    def on_release(key):
        nonlocal talking
        if key == talk_key and talking:
            talking = False
            audio = recorder.stop()
            print("[talk] transcribing…")
            text = transcribe_audio(audio, model_name=whisper_model)

            if not text:
                print("[talk] no transcript.")
                return

            print(f"\nyou: {text}\n")
            reply = chat.ask(text).strip()
            print(f"ollama: {reply}\n")
            speak(reply, voice=tts_voice)

    print("\nvoice-console (ollama ptt)")
    print("hold SPACE to talk. release to send. ctrl+c to quit.\n")
    print(f"whisper: {whisper_model} | ollama: {chat.model}\n")

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            pass

    print("\nbye.\n")


if __name__ == "__main__":
    main()