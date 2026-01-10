"""Characterization tests for pyaudioop sample bounds functions.

These tests capture the exact behavior of _get_minval(), _get_maxval(),
and _struct_format() before refactoring to lookup tables.
"""

from pydub.pyaudioop import _get_maxval, _get_minval, _struct_format


class TestGetMaxval:
    """Test _get_maxval() for all size/signed combinations."""

    def test_signed_8bit(self):
        assert _get_maxval(1, signed=True) == 0x7F  # 127

    def test_unsigned_8bit(self):
        assert _get_maxval(1, signed=False) == 0xFF  # 255

    def test_signed_16bit(self):
        assert _get_maxval(2, signed=True) == 0x7FFF  # 32767

    def test_unsigned_16bit(self):
        assert _get_maxval(2, signed=False) == 0xFFFF  # 65535

    def test_signed_32bit(self):
        assert _get_maxval(4, signed=True) == 0x7FFFFFFF  # 2147483647

    def test_unsigned_32bit(self):
        assert _get_maxval(4, signed=False) == 0xFFFFFFFF  # 4294967295


class TestGetMinval:
    """Test _get_minval() for all size/signed combinations."""

    def test_signed_8bit(self):
        assert _get_minval(1, signed=True) == -0x80  # -128

    def test_unsigned_8bit(self):
        assert _get_minval(1, signed=False) == 0

    def test_signed_16bit(self):
        assert _get_minval(2, signed=True) == -0x8000  # -32768

    def test_unsigned_16bit(self):
        assert _get_minval(2, signed=False) == 0

    def test_signed_32bit(self):
        assert _get_minval(4, signed=True) == -0x80000000  # -2147483648

    def test_unsigned_32bit(self):
        assert _get_minval(4, signed=False) == 0


class TestStructFormat:
    """Test _struct_format() for all size/signed combinations."""

    def test_signed_8bit(self):
        assert _struct_format(1, signed=True) == "b"

    def test_unsigned_8bit(self):
        assert _struct_format(1, signed=False) == "B"

    def test_signed_16bit(self):
        assert _struct_format(2, signed=True) == "h"

    def test_unsigned_16bit(self):
        assert _struct_format(2, signed=False) == "H"

    def test_signed_32bit(self):
        assert _struct_format(4, signed=True) == "i"

    def test_unsigned_32bit(self):
        assert _struct_format(4, signed=False) == "I"
