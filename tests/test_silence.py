"""Tests for silence detection and manipulation in pydub."""

import pytest

from pydub import AudioSegment
from pydub.silence import detect_silence, split_on_silence


@pytest.fixture(scope="module")
def silence_test_files(data_dir):
    """Load audio files used in silence tests."""
    test1_wav = AudioSegment.from_wav(str(data_dir / "test1.wav"))
    test4_wav = AudioSegment.from_wav(str(data_dir / "test4.wav"))
    return test1_wav, test4_wav


def test_split_on_silence_complete_silence():
    """Test splitting on silence with a completely silent segment."""
    seg = AudioSegment.silent(5000)
    assert split_on_silence(seg) == []


def test_split_on_silence_test1(silence_test_files):
    """Test splitting on silence in a test file."""
    test1, _ = silence_test_files
    splits = split_on_silence(test1, min_silence_len=500, silence_thresh=-20)
    assert len(splits) == 3


def test_split_on_silence_no_silence(silence_test_files):
    """Test splitting with threshold that finds no silence."""
    test1, _ = silence_test_files
    splits = split_on_silence(test1, min_silence_len=5000, silence_thresh=-200, keep_silence=True)
    lens = [len(split) for split in splits]
    assert lens == [len(test1)]


def test_detect_completely_silent_segment():
    """Test detecting silence in a completely silent segment."""
    seg = AudioSegment.silent(5000)
    silent_ranges = detect_silence(seg, min_silence_len=1000, silence_thresh=-20)
    assert silent_ranges == [[0, 5000]]


def test_detect_tight_silent_segment():
    """Test detecting silence in a segment exactly matching the min length."""
    seg = AudioSegment.silent(1000)
    silent_ranges = detect_silence(seg, min_silence_len=1000, silence_thresh=-20)
    assert silent_ranges == [[0, 1000]]


def test_detect_too_long_silence():
    """Test detecting silence with min length longer than the segment."""
    seg = AudioSegment.silent(3000)
    silent_ranges = detect_silence(seg, min_silence_len=5000, silence_thresh=-20)
    assert silent_ranges == []


def test_detect_silence_seg1(silence_test_files):
    """Test detecting silence in test1.wav."""
    test1, _ = silence_test_files
    silent_ranges = detect_silence(test1, min_silence_len=500, silence_thresh=-20)
    assert silent_ranges == [[0, 775], [3141, 4033], [5516, 6051]]


def test_detect_silence_seg1_with_seek_split(silence_test_files):
    """Test detecting silence with custom seek step."""
    test1, _ = silence_test_files
    silent_ranges = detect_silence(test1, min_silence_len=500, silence_thresh=-20, seek_step=10)
    assert silent_ranges == [[0, 770], [3150, 4030], [5520, 6050]]


def test_realistic_audio(silence_test_files):
    """Test silence detection on realistic audio sample."""
    _, test4 = silence_test_files
    silent_ranges = detect_silence(test4, min_silence_len=1000, silence_thresh=test4.dBFS)

    # Check that ranges are in order
    prev_end = -1
    for start, end in silent_ranges:
        assert start > prev_end
        prev_end = end
