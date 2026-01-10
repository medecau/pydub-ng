# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pydub-ng is a fork of Pydub focused on modern Python (3.10-3.13). It provides a high-level interface for audio manipulation using an immutable `AudioSegment` class.

**External dependency**: ffmpeg or libav required for non-WAV formats.

## Development Commands

```bash
# Install for development
pip install -e ".[dev]"

# Run all tests (via tox, multiple Python versions)
make test

# Run tests directly (faster for development)
pytest tests/ -v

# Run specific test file
pytest tests/test_utils.py -v

# Run tests matching pattern
pytest -k "test_db"

# Coverage report
make coverage

# Format code
make fmt

# Lint check
make lint
```

## Architecture

### Core Class: AudioSegment (`pydub/audio_segment.py`)

The central immutable class. All operations return new instances via the `_spawn()` method.

**Key attributes**: `sample_width`, `frame_rate`, `channels`, `_data` (raw bytes)

**Operator overloading**:
- `+` concatenates segments or applies gain (dB)
- `[:]` slices by milliseconds
- `*` repeats
- `len()` returns duration in milliseconds

### Effect Registration System (`pydub/effects.py`, `pydub/utils.py`)

Effects are functions decorated with `@register_pydub_effect`, which adds them as methods to `AudioSegment` at import time:

```python
@register_pydub_effect
def normalize(seg, headroom=0.1):
    ...
```

### Module Layout

- `audio_segment.py` - Core AudioSegment class and file I/O
- `effects.py` - Basic DSP effects (normalize, speedup, filters, compression)
- `scipy_effects.py` - SciPy-based effects (Butterworth filters, EQ) - auto-imported if scipy available
- `generators.py` - Signal generators (Sine, Square, Sawtooth, WhiteNoise)
- `silence.py` - Silence detection and splitting
- `playback.py` - Audio playback (simpleaudio → pyaudio → ffplay)
- `utils.py` - ffmpeg/ffprobe helpers, dB conversion, chunking
- `pyaudioop.py` - Pure Python audioop fallback for Python 3.13+

### Audio Processing Flow

1. **Loading**: `from_file()` uses ffmpeg to convert any format to WAV, then parses raw PCM
2. **Manipulation**: Operations use `audioop` (or `pyaudioop` fallback) for DSP, return new segments via `_spawn()`
3. **Export**: `export()` writes WAV to temp file, invokes ffmpeg for format conversion

## Testing

Tests use pytest with fixtures in `tests/conftest.py`. Test audio files are in `tests/data/`.

Debug ffmpeg issues with logging:
```python
import logging
l = logging.getLogger("pydub.converter")
l.setLevel(logging.DEBUG)
l.addHandler(logging.StreamHandler())
```
