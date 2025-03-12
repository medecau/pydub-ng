"""Tests for sound generators in pydub."""

import pytest

from pydub.generators import (
    Pulse,
    Sawtooth,
    Sine,
    Square,
    Triangle,
    WhiteNoise,
)


def test_generators_smoke():
    """Basic smoke test that generators produce audio segments."""
    Sine(440).to_audio_segment()
    Square(440).to_audio_segment()
    Triangle(440).to_audio_segment()
    Pulse(440, duty_cycle=0.75).to_audio_segment()
    Sawtooth(440, duty_cycle=0.75).to_audio_segment()
    WhiteNoise().to_audio_segment()


def test_loudness():
    """Test that generators produce audio with expected loudness."""
    sine_dbfs = Sine(440).to_audio_segment().dBFS
    square_dbfs = Square(440).to_audio_segment().dBFS
    white_noise_dbfs = WhiteNoise().to_audio_segment().dBFS

    assert pytest.approx(sine_dbfs, abs=0.1) == -3.0
    assert pytest.approx(square_dbfs, abs=0.1) == 0.0
    assert pytest.approx(white_noise_dbfs, abs=0.5) == -5


def test_duration():
    """Test that generators produce audio segments with expected duration."""
    one_sec = Sine(440).to_audio_segment(duration=1000)
    five_sec = Sine(440).to_audio_segment(duration=5000)
    half_sec = Sine(440).to_audio_segment(duration=500)

    assert len(one_sec) == pytest.approx(1000)
    assert len(five_sec) == pytest.approx(5000)
    assert len(half_sec) == pytest.approx(500)
