import os
from pathlib import Path

import pytest

from pydub import AudioSegment


@pytest.fixture(scope="session")
def data_dir():
    """Return the path to the test data directory."""
    return Path(os.path.join(os.path.dirname(__file__), "data"))


@pytest.fixture(scope="session")
def audio_file_mp3(data_dir):
    """Return the path to a test MP3 file."""
    return data_dir / "test1.mp3"


@pytest.fixture(scope="session")
def audio_file_wav(data_dir):
    """Return the path to a test WAV file."""
    return data_dir / "test1.wav"


@pytest.fixture(scope="session")
def audio_segment_mp3(audio_file_mp3):
    """Return an AudioSegment instance from an MP3 file."""
    return AudioSegment.from_file(str(audio_file_mp3), format="mp3")


@pytest.fixture(scope="session")
def audio_segment_wav(audio_file_wav):
    """Return an AudioSegment instance from a WAV file."""
    return AudioSegment.from_file(str(audio_file_wav), format="wav")


@pytest.fixture
def dummy_audio_segment():
    """Return a simple synthesized audio segment for testing."""
    # Create a silent segment and add some data to it
    duration = 2000  # ms
    sample_rate = 44100
    channels = 2

    return AudioSegment.silent(duration=duration, frame_rate=sample_rate).set_channels(channels)
