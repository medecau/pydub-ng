"""Smoke tests - verify all public modules import successfully.

These tests run first to catch import errors before running the full suite.
"""


def test_public_imports():
    """Verify all public modules can be imported."""
    # Imports
    import pydub
    from pydub import AudioSegment, effects, exceptions, generators, playback, silence, utils

    # Assertions
    assert pydub.AudioSegment is not None
    assert AudioSegment is not None
    assert effects is not None
    assert exceptions is not None
    assert generators is not None
    assert playback is not None
    assert silence is not None
    assert utils is not None
