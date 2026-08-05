# 🎙️ meeting-live-translate

> *Because "wait, what did they just say?" is not a valid meeting strategy.*

I'm an intern at a Chinese teleconsultation startup, and my Mandarin is currently sitting somewhere between "I can order noodles" and "I understood 30% of that all-hands." So I built the thing I actually needed: **live Mandarin → English captions, streaming straight off my mic, no cloud, no drama.**

Built by someone learning Chinese *while* working in Chinese, for anyone else surviving the same beautiful chaos. 🇫🇷🇲🇦➡️🇨🇳

---

## What this actually does

Someone talks in Mandarin → `whisper-stream` (whisper.cpp, Metal-accelerated, because my MacBook Air deserves to flex) transcribes it live → a filter layer throws out the noise and hallucinated garbage whisper sometimes makes up → Ollama (`qwen2.5:1.5b`, running fully local because I don't need my meeting notes anywhere near the internet) translates it into clean English → you get captions, in real time, while you nod along pretending you understood the joke someone just made.

```
🎤 Mandarin speech
   ↓ whisper-stream (Metal GPU)
📝 Raw transcript (with noise)
   ↓ hallucination + noise filters
✨ Clean Chinese text
   ↓ Ollama · qwen2.5:1.5b
🇬🇧 English captions
```

## Why local, why not just use [insert cloud API]

Because it's running during actual work meetings, and "actual work meetings" and "random third-party API" don't belong in the same sentence when you're an intern. Everything stays on-device. Slower model, sure — but I'm not shipping my boss's roadmap discussion to a server somewhere to save two seconds.

## Setup

You'll need:
- A Mac with Apple Silicon (this leans on Metal — sorry, Intel friends)
- `whisper.cpp` built with the `whisper-stream` binary
- [Ollama](https://ollama.com) installed, with `qwen2.5:1.5b` pulled
- Python 3.x + the usual `pip install -r requirements.txt`

```bash
# clone this repo
git clone https://github.com/AMINA-ELHASNAOUY/meeting-live-translate.git
cd meeting-live-translate

# grab whisper.cpp separately (not committed — it's a beast)
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp && cmake -B build && cmake --build build --config Release
./models/download-ggml-model.sh small
cd ..

# pull the translation model
ollama pull qwen2.5:1.5b

# install python deps
pip install -r requirements.txt

# run it
python main.py
```

## The filtering logic (aka keeping whisper honest)

whisper-stream is great but it *will* hallucinate — repeating phrases, inventing sentences during silence, throwing in its own log lines like they're part of the transcript. So before anything hits translation, it has to survive:

- **Noise prefix filtering** — kills whisper's own status/log lines (`main:`, `whisper_`, `[Start`, etc.)
- **Hallucination pattern matching** — filters out the classic repeated-phrase loops
- **Real content check** — needs at least 3 actual Chinese characters to bother translating. No characters, no translation, no wasted GPU cycles.

Only then does it get the strict translation prompt (temperature `0.1`, because this is not the moment for Ollama's creative writing era):

```
You are a translation engine, not a chat assistant.
Translate the Chinese sentence below into English.
Output ONLY the translation. No greetings, no explanations, no questions back to the user.
```

## Status

🟢 Running, streaming, producing output. Actively tuning the filters because meetings are messy and whisper has *opinions*.

## Roadmap (aka things I'll do when I stop procrastinating)

- [ ] Better hallucination detection (whisper really likes to loop on silence)
- [ ] On-screen caption overlay instead of terminal output
- [ ] Save transcripts + translations to a file for later review
- [ ] Support more target languages (French and Arabic, obviously — a girl's gotta represent)
- [ ] Maybe a tiny UI, because staring at a terminal during a meeting is a whole vibe but not a *professional* one

## A note on the vibe of this repo

This was built between class, an internship, teaching English to seven-year-olds, and studying for HSK 4 — so if a commit message is unhinged, that's the timestamp talking, not me. The code, however, is held to a much higher standard than my Tuesday nights. 💻✨

---

*Built with whisper.cpp, Ollama, and a genuine need to know what's happening in the group chat.*
