"""Tests for audio filters in pydub."""

import pytest

from pydub import AudioSegment
from pydub.generators import Sine, Square


@pytest.fixture
def audio_segment(data_dir):
    """Return an audio segment for testing filters."""
    return AudioSegment.from_wav(str(data_dir / "test1.wav"))


def test_highpass_works_on_multichannel_segments(audio_segment):
    """Test high-pass filter works on stereo audio."""
    assert audio_segment.channels == 2
    less_bass = audio_segment.high_pass_filter(800)
    assert less_bass.dBFS < audio_segment.dBFS


def test_highpass_filter_reduces_loudness():
    """Test high-pass filter reduces overall loudness."""
    s = Square(200).to_audio_segment()
    less_bass = s.high_pass_filter(400)
    assert less_bass.dBFS < s.dBFS


def test_highpass_filter_cutoff_frequency():
    """Test high-pass filter cutoff frequency behavior."""
    # A Sine wave should not be affected by a HPF 3 octaves lower
    s = Sine(800).to_audio_segment()
    less_bass = s.high_pass_filter(100)

    # The filter causes a slight reduction in volume, so we need a larger tolerance
    assert less_bass.dBFS == pytest.approx(s.dBFS, abs=0.15)


def test_lowpass_filter_reduces_loudness():
    """Test low-pass filter reduces overall loudness."""
    s = Square(200).to_audio_segment()
    less_treble = s.low_pass_filter(400)
    assert less_treble.dBFS < s.dBFS


def test_lowpass_filter_cutoff_frequency():
    """Test low-pass filter cutoff frequency behavior."""
    # A Sine wave should not be affected by a LPF 3 octaves higher
    s = Sine(100).to_audio_segment()
    less_treble = s.low_pass_filter(800)
    assert less_treble.dBFS == pytest.approx(s.dBFS, abs=0.1)
