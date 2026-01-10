"""Characterization tests for start_second/duration parameter behavior.

These tests capture the current behavior of from_file() and from_file_using_temporary_files()
with respect to start_second and duration parameters before refactoring to a helper function.
"""

import pytest

from pydub import AudioSegment


@pytest.fixture
def test_file():
    """Return path to a test audio file."""
    return "tests/data/test1.mp3"


class TestTimeSlicingFromFile:
    """Test start_second/duration behavior in from_file()."""

    def test_no_params_returns_full_audio(self, test_file):
        """When no time params are provided, full audio is returned."""
        result = AudioSegment.from_file(test_file)
        assert len(result) > 0
        # Verify it's the full length
        full_length = len(result)
        assert full_length > 1000  # test1.mp3 is more than 1 second

    def test_start_only(self, test_file):
        """When only start_second is provided, return audio from that point to end."""
        original = AudioSegment.from_file(test_file)
        result = AudioSegment.from_file(test_file, start_second=1)
        # Should be original length minus 1 second (1000ms)
        assert len(result) == len(original) - 1000

    def test_duration_only(self, test_file):
        """When only duration is provided, return audio from start with that duration."""
        result = AudioSegment.from_file(test_file, duration=2)
        # Should be exactly 2 seconds (2000ms)
        assert len(result) == 2000

    def test_start_and_duration(self, test_file):
        """When both are provided, return slice from start_second for duration."""
        result = AudioSegment.from_file(test_file, start_second=1, duration=2)
        # Should be exactly 2 seconds (2000ms) starting at 1s
        assert len(result) == 2000

    def test_edge_case_zero_duration(self, test_file):
        """Duration of 0 should return empty audio."""
        result = AudioSegment.from_file(test_file, duration=0)
        assert len(result) == 0

    def test_edge_case_start_at_zero(self, test_file):
        """start_second=0 with duration should work correctly."""
        result = AudioSegment.from_file(test_file, start_second=0, duration=1)
        assert len(result) == 1000


class TestTimeSlicingFromFileUsingTemporaryFiles:
    """Test start_second/duration behavior in from_file_using_temporary_files()."""

    def test_no_params_returns_full_audio(self, test_file):
        """When no time params are provided, full audio is returned."""
        result = AudioSegment.from_file_using_temporary_files(test_file)
        assert len(result) > 0
        full_length = len(result)
        assert full_length > 1000

    def test_start_only(self, test_file):
        """When only start_second is provided, return audio from that point to end."""
        original = AudioSegment.from_file_using_temporary_files(test_file)
        result = AudioSegment.from_file_using_temporary_files(test_file, start_second=1)
        assert len(result) == len(original) - 1000

    def test_duration_only(self, test_file):
        """When only duration is provided, return audio from start with that duration."""
        result = AudioSegment.from_file_using_temporary_files(test_file, duration=2)
        assert len(result) == 2000

    def test_start_and_duration(self, test_file):
        """When both are provided, return slice from start_second for duration."""
        result = AudioSegment.from_file_using_temporary_files(test_file, start_second=1, duration=2)
        assert len(result) == 2000

    def test_edge_case_zero_duration(self, test_file):
        """Duration of 0 should return empty audio."""
        result = AudioSegment.from_file_using_temporary_files(test_file, duration=0)
        assert len(result) == 0


class TestTimeSlicingEquivalence:
    """Verify both methods produce identical results for the same parameters."""

    @pytest.mark.parametrize(
        "start,duration",
        [
            (None, None),
            (1, None),
            (None, 2),
            (1, 2),
            (0, 1),
        ],
    )
    def test_methods_produce_same_length(self, test_file, start, duration):
        """Both from_file methods should produce same length output for same params."""
        result1 = AudioSegment.from_file(test_file, start_second=start, duration=duration)
        result2 = AudioSegment.from_file_using_temporary_files(
            test_file, start_second=start, duration=duration
        )
        assert len(result1) == len(result2)
