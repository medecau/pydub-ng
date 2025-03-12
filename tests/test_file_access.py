"""Tests for file access functionality in pydub."""

from pydub import AudioSegment


def test_audio_segment_from_mp3(data_dir):
    """Test AudioSegment creation from MP3 file."""
    mp3_path = data_dir / "test1.mp3"

    # Test with file path
    seg1 = AudioSegment.from_mp3(str(mp3_path))

    # Test with file object
    with open(mp3_path, "rb") as mp3_file:
        seg2 = AudioSegment.from_mp3(mp3_file)

    assert len(seg1) == len(seg2)
    assert seg1._data == seg2._data
    assert len(seg1) > 0
