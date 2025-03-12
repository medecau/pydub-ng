"""Tests for pydub functionality without an external converter."""

import pytest

from pydub import AudioSegment
from pydub.exceptions import MissingAudioParameter


@pytest.fixture(scope="module")
def test_files(data_dir):
    """Return paths to test files."""
    return {
        "wave_file": data_dir / "test1.wav",
        "wave24_file": data_dir / "test1-24bit.wav",
        "wave_empty": data_dir / "test1_empty.wav",
        "mp3_file": data_dir / "test1.mp3",
        "raw_file": data_dir / "test1.raw",
    }


@pytest.fixture
def no_converter():
    """Set a dummy converter path and restore the original after the test."""
    original_converter = AudioSegment.converter
    AudioSegment.converter = "definitely-not-a-path-to-anything-asdjklqwop"
    yield
    AudioSegment.converter = original_converter


def test_opening_wav_file(test_files, no_converter):
    """Test opening a WAV file works without a converter."""
    wave_file = test_files["wave_file"]

    seg = AudioSegment.from_wav(str(wave_file))
    assert len(seg) > 1000

    seg = AudioSegment.from_file(str(wave_file))
    assert len(seg) > 1000

    seg = AudioSegment.from_file(str(wave_file), "wav")
    assert len(seg) > 1000

    seg = AudioSegment.from_file(str(wave_file), format="wav")
    assert len(seg) > 1000


def test_opening_wav24_file(test_files, no_converter):
    """Test opening a 24-bit WAV file works without a converter."""
    wave24_file = test_files["wave24_file"]

    seg = AudioSegment.from_wav(str(wave24_file))
    assert len(seg) > 1000

    seg = AudioSegment.from_file(str(wave24_file))
    assert len(seg) > 1000

    seg = AudioSegment.from_file(str(wave24_file), "wav")
    assert len(seg) > 1000

    seg = AudioSegment.from_file(str(wave24_file), format="wav")
    assert len(seg) > 1000


def test_opening_raw_file(test_files, no_converter):
    """Test opening a RAW file works without a converter."""
    raw_file = test_files["raw_file"]

    seg = AudioSegment.from_raw(str(raw_file), sample_width=2, frame_rate=32000, channels=2)
    assert len(seg) > 1000

    seg = AudioSegment.from_file(str(raw_file), "raw", sample_width=2, frame_rate=32000, channels=2)
    assert len(seg) > 1000

    seg = AudioSegment.from_file(
        str(raw_file), format="raw", sample_width=2, frame_rate=32000, channels=2
    )
    assert len(seg) > 1000


def test_opening_raw_file_with_missing_args_fails(test_files, no_converter):
    """Test opening a RAW file fails without required args."""
    raw_file = test_files["raw_file"]

    with pytest.raises(KeyError):
        AudioSegment.from_raw(str(raw_file))


def test_opening_mp3_file_fails(test_files, no_converter):
    """Test opening an MP3 file fails without a converter."""
    mp3_file = test_files["mp3_file"]

    with pytest.raises(OSError):
        AudioSegment.from_mp3(str(mp3_file))

    with pytest.raises(OSError):
        AudioSegment.from_file(str(mp3_file))

    with pytest.raises(OSError):
        AudioSegment.from_file(str(mp3_file), "mp3")

    with pytest.raises(OSError):
        AudioSegment.from_file(str(mp3_file), format="mp3")


def test_init_audiosegment_data_buffer(no_converter):
    """Test creating an AudioSegment from a data buffer."""
    seg = AudioSegment(data=b"\0" * 34, sample_width=2, frame_rate=4, channels=1)

    assert seg.duration_seconds == 4.25
    assert seg.sample_width == 2
    assert seg.frame_rate == 4


def test_init_audiosegment_data_buffer_with_missing_args_fails(no_converter):
    """Test creating an AudioSegment fails without required args."""
    with pytest.raises(MissingAudioParameter):
        AudioSegment(data=b"\0" * 16, sample_width=2, frame_rate=2)

    with pytest.raises(MissingAudioParameter):
        AudioSegment(data=b"\0" * 16, sample_width=2, channels=1)

    with pytest.raises(MissingAudioParameter):
        AudioSegment(data=b"\0" * 16, frame_rate=2, channels=1)


def test_init_audiosegment_data_buffer_with_bad_values_fails(no_converter):
    """Test creating an AudioSegment fails with invalid data size."""
    with pytest.raises(ValueError):
        AudioSegment(data=b"\0" * 14, sample_width=4, frame_rate=2, channels=1)


def test_exporting(test_files, no_converter):
    """Test exporting works without a converter."""
    wave_file = test_files["wave_file"]

    seg = AudioSegment.from_wav(str(wave_file))
    exported = AudioSegment.from_wav(seg.export(format="wav"))

    assert len(exported) == len(seg)


def test_opening_empty_wav_file(test_files, no_converter):
    """Test opening an empty WAV file works without a converter."""
    wave_empty = test_files["wave_empty"]

    seg = AudioSegment.from_wav(str(wave_empty))
    assert len(seg) == 0

    seg = AudioSegment.from_file(str(wave_empty))
    assert len(seg) == 0

    seg = AudioSegment.from_file(str(wave_empty), "wav")
    assert len(seg) == 0

    seg = AudioSegment.from_file(str(wave_empty), format="wav")
    assert len(seg) == 0
