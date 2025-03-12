"""Tests for partial loading of audio segments."""

import pytest

from pydub import AudioSegment


@pytest.fixture
def audio_paths(data_dir):
    """Return paths to audio files for testing partial loading."""
    return {
        "mp3": str(data_dir / "test1.mp3"),
        "wav": str(data_dir / "test1.wav"),
        "raw": str(data_dir / "test1.raw"),
    }


def test_partial_load_duration_equals_cropped_mp3_audio_segment(audio_paths):
    """Test partial loading duration parameter with MP3."""
    mp3_path = audio_paths["mp3"]
    partial_seg1 = AudioSegment.from_file(mp3_path)[:1000]
    partial_seg2 = AudioSegment.from_file(mp3_path, duration=1.0)
    assert len(partial_seg1) == len(partial_seg2)
    assert partial_seg1._data == partial_seg2._data


def test_partial_load_start_second_equals_cropped_mp3_audio_segment(audio_paths):
    """Test partial loading start_second parameter with MP3."""
    mp3_path = audio_paths["mp3"]
    partial_seg1 = AudioSegment.from_file(mp3_path)[1000:]
    partial_seg2 = AudioSegment.from_file(mp3_path, start_second=1.0)[0:]
    assert len(partial_seg1) == len(partial_seg2)
    assert partial_seg1._data == partial_seg2._data


def test_partial_load_start_second_and_duration_equals_cropped_mp3_audio_segment(
    audio_paths,
):
    """Test partial loading with both start_second and duration with MP3."""
    mp3_path = audio_paths["mp3"]
    partial_seg1 = AudioSegment.from_file(mp3_path)[1000:2000]
    partial_seg2 = AudioSegment.from_file(mp3_path, start_second=1.0, duration=1.0)
    assert len(partial_seg1) == len(partial_seg2)
    assert partial_seg1._data == partial_seg2._data


def test_partial_load_duration_equals_cropped_wav_audio_segment(audio_paths):
    """Test partial loading duration parameter with WAV."""
    wav_path = audio_paths["wav"]
    partial_seg1 = AudioSegment.from_file(wav_path)[:1000]
    partial_seg2 = AudioSegment.from_file(wav_path, duration=1.0)
    assert len(partial_seg1) == len(partial_seg2)
    assert partial_seg1._data == partial_seg2._data


def test_partial_load_start_second_equals_cropped_wav_audio_segment(audio_paths):
    """Test partial loading start_second parameter with WAV."""
    wav_path = audio_paths["wav"]
    partial_seg1 = AudioSegment.from_file(wav_path)[1000:]
    partial_seg2 = AudioSegment.from_file(wav_path, start_second=1.0)[0:]
    assert len(partial_seg1) == len(partial_seg2)
    assert partial_seg1._data == partial_seg2._data


def test_partial_load_start_second_and_duration_equals_cropped_wav_audio_segment(
    audio_paths,
):
    """Test partial loading with both start_second and duration with WAV."""
    wav_path = audio_paths["wav"]
    partial_seg1 = AudioSegment.from_file(wav_path)[1000:2000]
    partial_seg2 = AudioSegment.from_file(wav_path, start_second=1.0, duration=1.0)
    assert len(partial_seg1) == len(partial_seg2)
    assert partial_seg1._data == partial_seg2._data


def test_partial_load_duration_equals_cropped_raw_audio_segment(audio_paths):
    """Test partial loading duration parameter with RAW."""
    raw_path = audio_paths["raw"]
    partial_seg1 = AudioSegment.from_file(
        raw_path,
        format="raw",
        sample_width=2,
        frame_rate=32000,
        channels=2,
    )[:1000]
    partial_seg2 = AudioSegment.from_file(
        raw_path,
        format="raw",
        sample_width=2,
        frame_rate=32000,
        channels=2,
        duration=1.0,
    )
    assert len(partial_seg1) == len(partial_seg2)
    assert partial_seg1._data == partial_seg2._data


def test_partial_load_start_second_equals_cropped_raw_audio_segment(audio_paths):
    """Test partial loading start_second parameter with RAW."""
    raw_path = audio_paths["raw"]
    partial_seg1 = AudioSegment.from_file(
        raw_path,
        format="raw",
        sample_width=2,
        frame_rate=32000,
        channels=2,
    )[1000:]
    partial_seg2 = AudioSegment.from_file(
        raw_path,
        format="raw",
        sample_width=2,
        frame_rate=32000,
        channels=2,
        start_second=1.0,
    )[0:]
    assert len(partial_seg1) == len(partial_seg2)
    assert partial_seg1._data == partial_seg2._data


def test_partial_load_start_second_and_duration_equals_cropped_raw_audio_segment(
    audio_paths,
):
    """Test partial loading with both start_second and duration with RAW."""
    raw_path = audio_paths["raw"]
    partial_seg1 = AudioSegment.from_file(
        raw_path,
        format="raw",
        sample_width=2,
        frame_rate=32000,
        channels=2,
    )[1000:2000]
    partial_seg2 = AudioSegment.from_file(
        raw_path,
        format="raw",
        sample_width=2,
        frame_rate=32000,
        channels=2,
        start_second=1.0,
        duration=1.0,
    )
    assert len(partial_seg1) == len(partial_seg2)
    assert partial_seg1._data == partial_seg2._data
