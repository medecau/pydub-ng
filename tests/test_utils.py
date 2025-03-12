"""Tests for pydub utility functions."""

from pydub.utils import (
    db_to_float,
    get_encoder_name,
    get_supported_decoders,
    make_chunks,
    ratio_to_db,
)


def test_db_float_conversions():
    """Test the conversion between decibels and float values."""
    assert db_to_float(20) == 10
    assert db_to_float(10, using_amplitude=False) == 10
    assert db_to_float(0) == 1
    assert ratio_to_db(1) == 0
    assert ratio_to_db(10) == 20
    assert ratio_to_db(10, using_amplitude=False) == 10
    assert 3 == db_to_float(ratio_to_db(3))


def test_supported_formats_decoder():
    """Test that we can get a list of supported decoders."""
    supported_formats = get_supported_decoders()
    # Just test that we get a non-empty set of decoders
    assert isinstance(supported_formats, set)
    assert len(supported_formats) > 0


def test_get_encoder_name():
    """Test getting encoder application name."""
    encoder_name = get_encoder_name()
    # Should return either ffmpeg or avconv
    assert encoder_name in ["ffmpeg", "avconv"]


def test_make_chunks(dummy_audio_segment):
    """Test splitting an audio segment into chunks."""
    seg = dummy_audio_segment  # Fixture from conftest.py

    # Test chunk sizes
    chunk_sizes = [100, 200, 500]

    for chunk_size in chunk_sizes:
        chunks = make_chunks(seg, chunk_size)

        # Test that chunks add up to original segment (approximately)
        total_chunks_length = sum(len(chunk) for chunk in chunks)
        # May not be exactly equal due to rounding
        assert abs(total_chunks_length - len(seg)) < len(chunks)

        # Test that all chunks except the last one have the correct size
        for i, chunk in enumerate(chunks[:-1]):
            assert len(chunk) == chunk_size
