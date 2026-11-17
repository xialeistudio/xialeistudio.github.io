---
title: "Echoic: AI-Powered English Pronunciation Practice with Real-Time Phoneme-Level Scoring"
date: 2026-04-10T10:00:00+08:00
slug: echoic-ai-pronunciation-practice
categories:
- ai
tags:
- English Learning
- Pronunciation
- FastAPI
- React
featured: true
---

I recently open-sourced [Echoic](https://github.com/xialeistudio/echoic), an AI-powered tool for practicing English pronunciation. The core idea: import any audio, shadow it sentence by sentence, and get instant phoneme-level scoring.

<!--more-->

## Why I Built It

Existing pronunciation tools are either closed apps (you can't import your own material) or black-box scorers (they tell you "great" or "needs improvement" without saying which sound you got wrong).

What I wanted:
1. **Practice with content I actually like**: import any audio instead of being limited to a platform's content library
2. **Phoneme-level feedback**: not "this sentence was off", but "the 2nd phoneme of the 3rd word deviated"
3. **Offline use**: models run locally with no dependency on cloud services

## How It Works

The pipeline has four steps: **ASR → forced alignment → pronunciation scoring → AI analysis (optional)**.

### Speech Recognition: WhisperX

[WhisperX](https://github.com/m-bain/whisperX) runs ASR on the user's recording and outputs word-level results with timestamps. It is built on faster-whisper (CTranslate2 backend), so inference speed is acceptable even on CPU.

The model size is configurable: `base` is fine for daily use, while `large-v2` is more accurate but slower.

### Forced Alignment: wav2vec2

ASR only gives word-level timestamps. Getting to **phoneme-level alignment** takes a second step: forced alignment with wav2vec2, which maps each audio frame to a specific phoneme.

This step determines which phoneme was produced at which point in time, and everything downstream depends on it.

### Pronunciation Scoring

The scoring model is also based on wav2vec2 + phonemizer:

1. Extract the expected phoneme sequence from the reference text (phonemizer → IPA)
2. Extract the actual phoneme sequence from the user's recording (wav2vec2)
3. Align the two sequences with Levenshtein edit distance and compare them phoneme by phoneme

The output covers three dimensions:

| Dimension | Meaning |
|---|---|
| Accuracy | How closely the produced phonemes match the target phonemes |
| Fluency | Whether pauses and rhythm sound natural |
| Completeness | Whether any phonemes were dropped or added |

The three are combined into a weighted overall score, with weights configurable via environment variables.

### AI Analysis (Optional)

With the OpenAI API configured, each sentence gets a translation and a grammar breakdown. This is optional: without an API key it is skipped automatically, and the core pronunciation practice does not depend on an LLM at all.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, shadcn/ui, WaveSurfer.js |
| Backend | FastAPI, SQLAlchemy, Alembic |
| ASR | WhisperX (faster-whisper + CTranslate2) |
| Alignment | wav2vec2 |
| Scoring | wav2vec2 + phonemizer |
| Database | PostgreSQL 16 |

## Features

- **Audio import**: upload local files or import from a URL
- **Sentence-by-sentence practice**: adjustable playback speed, record your shadowing one sentence at a time
- **Phoneme display**: IPA transcription for every word
- **Real-time scoring**: accuracy, fluency, and completeness
- **Practice history**: every attempt is recorded so you can review your progress over time
- **Practice heatmap**: a 365-day activity view, just like the GitHub contribution graph
- **Sentence bookmarks**: mark key sentences for focused drilling

## Quick Start

Requirements: Python 3.11+, Node.js 20+, pnpm, PostgreSQL 16, ffmpeg, espeak-ng.

```bash
# macOS
brew install ffmpeg espeak-ng postgresql@16

# Clone the repository
git clone https://github.com/xialeistudio/echoic.git
cd echoic

# Start the database (Docker)
make db

# Backend
cd backend
uv sync
cp .env.example .env   # edit as needed
uv run alembic upgrade head
cd .. && make run

# Frontend (in another terminal)
make dev-frontend
```

Then open `http://localhost:5173`.

For production, run `make build` first to build the frontend. The output goes to `backend/static`, after which `make run` serves everything from `http://localhost:8000`.

## Design Decisions

**Why not cloud ASR?**

Cloud ASR (such as the Whisper API) adds network latency, and every practice session means uploading your recordings, which is bad for privacy. Running locally makes the first model load slow, but after that each scoring round takes under a second, which is a better experience.

**Why WhisperX instead of the original Whisper?**

WhisperX's forced alignment is the key. The original Whisper only provides word-level timestamps, which isn't enough for phoneme-level comparison. On top of that, WhisperX's CTranslate2 backend is 4-8x faster than the original Whisper.

**Why Levenshtein for scoring instead of a direct comparison?**

Learners inevitably drop or add sounds while practicing, so comparing by index would misalign everything after the first mistake. Levenshtein alignment handles insertions and deletions correctly and produces a more accurate phoneme-level match.

## Roadmap

- [ ] CUDA acceleration (currently CPU by default, which limits speed)
- [ ] Shadowing progress tracking (completion across a whole book or series)
- [ ] Phoneme weakness analysis (stats on which phonemes you keep getting wrong)
- [ ] Mobile support

## Source Code

GitHub: [xialeistudio/echoic](https://github.com/xialeistudio/echoic), MIT licensed. Stars and PRs are welcome.
