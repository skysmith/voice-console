#!/usr/bin/env python3
import os
import shlex
import subprocess
from dataclasses import dataclass

from stt import transcribe_from_mic
from tts import speak
from openclaw_client import ask_openclaw


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


@dataclass
class Settings:
    record_seconds: float
    whisper_model: str
    tts_voice: str | None
    openclaw_cmd_template: str


def get_settings() -> Settings:
    load_env("config.env")
    record_seconds = float(os.getenv("RECORD_SECONDS", "4"))
    whisper_model = os.getenv("WHISPER_MODEL", "small")
    tts_voice = os.getenv("TTS_VOICE") or None
    openclaw_cmd_template = os.getenv("OPENCLAW_CMD_TEMPLATE", 'openclaw chat "{prompt}"')
    return Settings(
        record_seconds=record_seconds,
        whisper_model=whisper_model,
        tts_voice=tts_voice,
        openclaw_cmd_template=openclaw_cmd_template,
    )


def main():
    s = get_settings()

    print("\nvoice-openclaw (minimal cli)")
    print("enter = record → transcribe → ask openclaw → speak reply")
    print("ctrl+c = quit\n")
    print(f"record: {s.record_seconds}s | whisper: {s.whisper_model}")
    print(f"openclaw template: {s.openclaw_cmd_template}\n")

    try:
        while True:
            input("[enter] talk… ")
            text = transcribe_from_mic(seconds=s.record_seconds, model_name=s.whisper_model).strip()
            if not text:
                print("no transcript.\n")
                continue

            print(f"\nyou: {text}\n")

            reply = ask_openclaw(text, s.openclaw_cmd_template).strip()
            if not reply:
                print("openclaw returned no text.\n")
                continue

            print(f"openclaw: {reply}\n")
            speak(reply, voice=s.tts_voice)

    except KeyboardInterrupt:
        print("\nbye.\n")


if __name__ == "__main__":
    main()