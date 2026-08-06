"""Live Chinese meeting captioning + translation — core pipeline.

Same filtering/translation logic as the original main.py, refactored into
a generator so it can be driven by either the terminal (main.py) or the
web UI (web_app.py) without duplicating any logic.
"""

import re
import subprocess
import requests

WHISPER_STREAM_BIN = "../whispermeet-ai-summarizer/whisper.cpp/build/bin/whisper-stream"
WHISPER_MODEL = "../whispermeet-ai-summarizer/whisper.cpp/models/ggml-small.bin"
OLLAMA_URL = "http://localhost:11434/api/generate"
TRANSLATE_MODEL = "qwen2.5:1.5b"  # small & fast, for low-latency live translation
TARGET_LANGUAGE = "English"  # change to "French" if you prefer

# Patterns whisper.cpp tends to hallucinate during silence/noise.
HALLUCINATION_PATTERNS = [
    r"字幕",
    r"謝謝(大家)?收看",
    r"謝謝觀看",
    r"下次見",
]

# Lines from whisper-stream's own logging/status output, not transcription.
NOISE_PREFIXES = (
    "main:", "whisper_", "ggml_", "init:", "[Start",
)


def is_hallucination(line: str) -> bool:
    return any(re.search(pattern, line) for pattern in HALLUCINATION_PATTERNS)


def has_real_content(line: str) -> bool:
    """Only translate lines that contain actual Chinese speech, not fragments."""
    chinese_chars = re.findall(r"[\u4e00-\u9fff]", line)
    return len(chinese_chars) >= 3


def translate_line(text: str) -> str:
    prompt = (
        f"You are a translation engine, not a chat assistant. "
        f"Translate the Chinese sentence below into {TARGET_LANGUAGE}. "
        f"Output ONLY the translation. No greetings, no explanations, "
        f"no questions back to the user.\n\n"
        f"Chinese: {text}\n"
        f"{TARGET_LANGUAGE}:"
    )
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": TRANSLATE_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1},
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("response", "").strip()


def listen():
    """Start whisper-stream and yield one event dict per meaningful line.

    Event shapes:
      {"type": "caption", "zh": "...", "en": "..."}
      {"type": "error", "message": "..."}
    Runs until the caller stops iterating (e.g. Ctrl+C or a stop flag) or
    whisper-stream's process ends.
    """
    process = subprocess.Popen(
        [WHISPER_STREAM_BIN, "-m", WHISPER_MODEL, "-l", "zh"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )

    try:
        for line in process.stdout:
            line = line.strip()

            if not line:
                continue
            if line.startswith(NOISE_PREFIXES):
                continue
            if is_hallucination(line):
                continue
            if not has_real_content(line):
                continue

            try:
                translated = translate_line(line)
                yield {"type": "caption", "zh": line, "en": translated}
            except requests.RequestException as exc:
                yield {"type": "error", "message": f"translation failed: {exc}"}
    finally:
        process.terminate()
