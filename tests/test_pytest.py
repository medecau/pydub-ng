from pydub import AudioSegment
from pydub.utils import db_to_float, ratio_to_db


def test_db_float_conversions():
    """Test the conversion between decibels and float values."""
    assert db_to_float(20) == 10
    assert db_to_float(10, using_amplitude=False) == 10
    assert db_to_float(0) == 1
    assert ratio_to_db(1) == 0
    assert ratio_to_db(10) == 20
    assert ratio_to_db(10, using_amplitude=False) == 10
    assert 3 == db_to_float(ratio_to_db(3))


def test_audio_segment_from_mp3(data_dir):
    """Test loading an MP3 file with AudioSegment."""
    mp3_path = data_dir / "test1.mp3"
    seg = AudioSegment.from_mp3(str(mp3_path))

    assert len(seg) > 0
    assert seg.duration_seconds > 0
    assert seg.channels == 2
    assert seg.frame_rate == 32000  # Actual sample rate of test1.mp3


def test_export_pathlib_path(data_dir, tmp_path):
    """Test exporting to a Path object."""
    mp3_path = data_dir / "test1.mp3"
    seg1 = AudioSegment.from_file(str(mp3_path))

    # Use pytest's tmp_path fixture to create a temporary file
    export_path = tmp_path / "exported.mp3"

    seg1.export(export_path, format="mp3")
    seg2 = AudioSegment.from_file(export_path, format="mp3")

    assert len(seg1) > 0
    # Check that lengths are within 1%
    assert abs(len(seg1) - len(seg2)) < len(seg1) * 0.01
