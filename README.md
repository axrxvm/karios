# Karios

> WORK IN PROGRESS — v0.1  
> Expect breaking changes, rough edges, and rapid iteration.

Karios is a local-first, voice-controlled AI assistant with intelligent intent routing.
It prioritizes on-device execution and privacy, falling back to an LLM only when necessary.

Built to be fast, extensible, and platform-agnostic.

## Why the name?

Karios is derived from *kairos* — the Greek concept of the “right” or opportune moment to act,
as opposed to linear or chronological time.
The name reflects the core design philosophy:
understand intent, respond at the right moment, and apply only as much intelligence as required —
whether that means executing a local command instantly or escalating to deeper reasoning.
> I didn't just misspelled the `i` and `r` when creating the folder...

## Features

- Local speech recognition (Vosk)
- Local text-to-speech synthesis (Piper)
- Intent-based routing with LLM fallback
- Cross-platform support (Windows, Linux, macOS)
- Native system command execution

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Install the `piper` CLI and download models under `models/`.
4. Copy `.env.example` to `.env` and set values.
5. Run:
   `python main.py`

## Configuration

Karios now expects configuration from `.env` (see `.env.example`):

- `KARIOS_DEBUG`
- `KARIOS_LOG_LEVEL`
- `KARIOS_LLM_ENABLED`
- `KARIOS_LLM_MODEL`
- `KARIOS_STT_SAMPLE_RATE`
- `KARIOS_WAKE_WORD`
- `KARIOS_VOSK_MODEL_PATH`
- `KARIOS_PIPER_MODEL_PATH`
- `KARIOS_ALLOW_POWER_ACTIONS`
- `KARIOS_REQUIRE_POWER_CONFIRMATION`

LLM credentials:

- `OPENAI_API_KEY` (required if `KARIOS_LLM_ENABLED=true`)
- `OPENAI_API_BASE` (optional)

## License

MIT License © 2026 Aarav Mehta
