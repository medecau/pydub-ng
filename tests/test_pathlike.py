"""Tests for path-like object handling in pydub."""

import sys
from pathlib import Path

import pytest

from pydub import AudioSegment


class MyPathLike:
    """Custom path-like object implementation for testing."""

    def __init__(self, path):
        self.path = path

    def __fspath__(self):
        return self.path


@pytest.fixture
def mp3_path_str(data_dir):
    """Return the path to a test MP3 file as string."""
    return str(data_dir / "test1.mp3")


@pytest.fixture
def mp3_pathlib_path(mp3_path_str):
    """Return the path to a test MP3 file as pathlib.Path."""
    return Path(mp3_path_str)


@pytest.fixture
def mp3_path_like_str(mp3_path_str):
    """Return the path to a test MP3 file as path-like object with string."""
    return MyPathLike(mp3_path_str)


@pytest.fixture
def mp3_path_like_bytes(mp3_path_str):
    """Return the path to a test MP3 file as path-like object with bytes."""
    return MyPathLike(bytes(mp3_path_str, sys.getdefaultencoding()))


def test_audio_segment_from_pathlib_path(mp3_path_str, mp3_pathlib_path):
    """Test creating AudioSegment from pathlib.Path object."""
    seg1 = AudioSegment.from_file(mp3_path_str)
    seg2 = AudioSegment.from_file(mp3_pathlib_path)

    assert len(seg1) == len(seg2)
    assert seg1._data == seg2._data
    assert len(seg1) > 0


def test_audio_segment_from_path_like_str(mp3_path_str, mp3_path_like_str):
    """Test creating AudioSegment from os.PathLike object with string."""
    seg1 = AudioSegment.from_file(mp3_path_str)
    seg2 = AudioSegment.from_file(mp3_path_like_str)

    assert len(seg1) == len(seg2)
    assert seg1._data == seg2._data
    assert len(seg1) > 0


def test_audio_segment_from_path_like_bytes(mp3_path_str, mp3_path_like_bytes):
    """Test creating AudioSegment from os.PathLike object with bytes."""
    seg1 = AudioSegment.from_file(mp3_path_str)
    seg2 = AudioSegment.from_file(mp3_path_like_bytes)

    assert len(seg1) == len(seg2)
    assert seg1._data == seg2._data
    assert len(seg1) > 0


def test_non_existent_pathlib_path():
    """Test behavior with non-existent pathlib.Path."""
    path = Path("this/path/should/not/exist/do/not/make/this/exist")
    with pytest.raises(FileNotFoundError):
        AudioSegment.from_file(path)

    path = Path("")
    # On Unicies this will raise a IsADirectoryError, on Windows this
    # will result in a PermissionError. Both of these are subclasses of
    # OSError. We aren't so much worried about the specific exception
    # here, just that reading a file from an empty path is an error.
    with pytest.raises(OSError):
        AudioSegment.from_file(path)


def test_non_existent_path_like_str():
    """Test behavior with non-existent path-like object with string."""
    path = MyPathLike("this/path/should/not/exist/do/not/make/this/exist")
    with pytest.raises(FileNotFoundError):
        AudioSegment.from_file(path)

    path = MyPathLike("")
    with pytest.raises(FileNotFoundError):
        AudioSegment.from_file(path)


def test_non_existent_path_like_bytes():
    """Test behavior with non-existent path-like object with bytes."""
    path = MyPathLike(
        bytes(
            "this/path/should/not/exist/do/not/make/this/exist",
            sys.getdefaultencoding(),
        )
    )
    with pytest.raises(FileNotFoundError):
        AudioSegment.from_file(path)

    path = MyPathLike(bytes("", sys.getdefaultencoding()))
    with pytest.raises(FileNotFoundError):
        AudioSegment.from_file(path)


def test_export_pathlib_path(data_dir, tmp_path):
    """Test exporting to a Path object."""
    mp3_path = data_dir / "test1.mp3"
    seg1 = AudioSegment.from_file(str(mp3_path))

    # Use pytest's tmp_path fixture to create a temporary file
    export_path = tmp_path / "pathlib-export-test.mp3"

    # Export to the temporary file
    seg1.export(export_path, format="mp3")
    seg2 = AudioSegment.from_file(export_path, format="mp3")

    # Check that the export was successful
    assert len(seg1) > 0
    # Check that lengths are within 1%
    assert abs(len(seg1) - len(seg2)) < len(seg1) * 0.01

    # tmp_path fixture automatically cleans up after the test
