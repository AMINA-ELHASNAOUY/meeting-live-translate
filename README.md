# 🎙️ meeting-live-translate

> *Because "wait, what did they just say?" is not a valid meeting strategy.*

I'm an intern at a Chinese teleconsultation startup, and my Mandarin is currently sitting somewhere between "I can order noodles" and "I understood 30% of that all-hands." So I built the thing I actually needed: **live Mandarin → English captions, streaming straight off my mic, no cloud, no drama.**

Built by someone learning Chinese *while* working in Chinese, for anyone else surviving the same beautiful chaos. 🇫🇷🇲🇦➡️🇨🇳

---

## What this actually does

Someone talks in Mandarin → `whisper-stream` (whisper.cpp, Metal-accelerated) transcribes it live → a filter layer strips out noise and hallucinated fragments → Ollama (`qwen2.5:1.5b`, running fully local) translates it into clean English → captions appear in real time, in your browser.

```
🎤 Mandarin speech
   ↓ whisper-stream (Metal GPU)
📝 Raw transcript (with noise)
   ↓ hallucination + noise filters
✨ Clean Chinese text
   ↓ Ollama · qwen2.5:1.5b
🇬🇧 English captions
```

## Why local, not a cloud API

This runs during actual work meetings, so "actual work meetings" and "third-party API" don't belong in the same sentence. Everything — audio, transcription, translation — stays on-device. It trades raw speed for the guarantee that nothing said in a meeting leaves the machine it was said on.

## Two ways to run it

**Browser (recommended)** — a live caption feed at `localhost:7860`, built with Flask + Server-Sent Events. Same pipeline underneath, nicer to actually watch during a meeting than a scrolling terminal.

**Terminal** — the original mode. Same filtering and translation logic, printed straight to stdout. Useful for quick debugging or headless runs.

Both modes share one core pipeline (`pipeline.py`), so there's no duplicated logic between them.

## Setup

You'll need:
- A Mac with Apple Silicon (this leans on Metal — sorry, Intel friends)
- `whisper.cpp` built with the `whisper-stream` binary
- [Ollama](https://ollama.com) installed, with `qwen2.5:1.5b` pulled
- Python 3.x

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

# set up a virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Run it:**

```bash
# browser mode — open http://localhost:7860 after this starts
python web_app.py

# terminal mode
python main.py
```

## The filtering logic (aka keeping whisper honest)

whisper-stream is fast but it *will* hallucinate — repeating phrases, inventing sentences during silence, mixing its own log output into the transcript. Before anything reaches translation, each line has to survive:

- **Noise prefix filtering** — drops whisper-stream's own status/log lines (`main:`, `whisper_`, `[Start`, etc.)
- **Hallucination pattern matching** — filters known repeated-phrase loops
- **Real content check** — requires at least 3 actual Chinese characters before bothering to translate

Only then does it get a strict translation prompt (temperature `0.1` — this is not the moment for creative writing):

```
You are a translation engine, not a chat assistant.
Translate the Chinese sentence below into English.
Output ONLY the translation. No greetings, no explanations, no questions back to the user.
```

## Known limitations

Being upfront about what this doesn't handle yet, because a tool is more trustworthy when its edges are documented:

- **ANSI escape codes can leak through** (e.g. stray `[2K` fragments) — whisper-stream sends terminal control codes meant for redrawing an interactive console, and they aren't stripped yet. Next on the fix list.
- **Small-model trade-off** — `qwen2.5:1.5b` is fast enough for live use, but on short or fragmented input it sometimes guesses rather than translates precisely. A larger model would improve accuracy at the cost of latency.
- **A few seconds of inherent lag** — whisper-stream only emits a line once it's finalized a segment, so captions trail live speech slightly. This is a whisper-stream behavior, not something the app layer can remove.
- **Domain vocabulary is untested** — hasn't yet been validated against real teleconsultation/medical-device terminology from actual work meetings.

## Status

🟢 Browser UI and terminal mode both running end-to-end. Currently validating it against real meetings before calling it daily-driver ready.

## Roadmap

- [x] Browser-based caption view (Flask + SSE)
- [ ] Strip ANSI escape codes at the filter layer
- [ ] Fix status indicator reliability on reconnect
- [ ] Save transcripts + translations to a file for later review
- [ ] Support more target languages (French and Arabic)
- [ ] Validate against real Pubwell meetings with actual domain vocabulary

## A note on the vibe of this repo

Built between class, an internship, teaching English to seven-year-olds, and studying for HSK 4 — so if a commit message is unhinged, that's the timestamp talking. The code, however, is held to a higher standard than my Tuesday nights. 💻✨

---

*Built with whisper.cpp, Ollama, and a genuine need to know what's happening in the group chat.*
