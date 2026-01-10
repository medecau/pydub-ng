"""Characterization tests for Python 3 features.

These tests verify that Python 3 behavior is in place before
removing Python 2 compatibility shims.
"""


def test_uses_python3_division():
    """Verify division returns float (Python 3 behavior)."""
    # In Python 2, 5 / 2 would return 2 (integer division)
    # In Python 3, 5 / 2 returns 2.5 (true division)
    assert 5 / 2 == 2.5


def test_basestring_not_used_in_audio_segment():
    """Python 3 uses str directly instead of basestring."""
    import pydub.audio_segment as mod

    # Should either not have basestring, or it should be aliased to str
    if hasattr(mod, "basestring"):
        assert mod.basestring is str


def test_basestring_not_used_in_utils():
    """Python 3 uses str directly in utils module."""
    import pydub.utils as mod

    # Should either not have basestring, or it should be aliased to str
    if hasattr(mod, "basestring"):
        assert mod.basestring is str


def test_xrange_not_used_in_audio_segment():
    """Python 3 uses range directly instead of xrange."""
    import pydub.audio_segment as mod

    # Should either not have xrange, or it should be aliased to range
    if hasattr(mod, "xrange"):
        assert mod.xrange is range


def test_xrange_not_used_in_effects():
    """Python 3 uses range directly in effects module."""
    import pydub.effects as mod

    # Should either not have xrange, or it should be aliased to range
    if hasattr(mod, "xrange"):
        assert mod.xrange is range
