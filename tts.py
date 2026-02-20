import subprocess


def speak(text: str, voice: str | None = None):
    # mac built-in
    cmd = ["say"]
    if voice:
        cmd += ["-v", voice]
    cmd += [text]
    subprocess.run(cmd, check=False)