"""Tests for scipy-based audio effects.

These tests require scipy to be installed and will be skipped otherwise.
"""

import pytest

# Skip entire module if scipy not available
scipy = pytest.importorskip("scipy", reason="scipy required for scipy_effects tests")

from pydub.generators import Sine

# scipy_effects is now auto-imported by pydub.__init__ if scipy is available


class TestScipyImportError:
    """Test that scipy_effects provides helpful error when scipy missing."""

    def test_import_error_message_is_helpful(self, monkeypatch):
        """Importing scipy_effects without scipy should give clear guidance."""
        import sys

        # Remove scipy from available modules
        monkeypatch.setitem(sys.modules, "scipy", None)
        monkeypatch.setitem(sys.modules, "scipy.signal", None)

        # Force reimport of scipy_effects
        if "pydub.scipy_effects" in sys.modules:
            del sys.modules["pydub.scipy_effects"]

        with pytest.raises(ImportError) as exc_info:
            import pydub.scipy_effects

        # Should mention how to install scipy
        assert "scipy" in str(exc_info.value).lower()
        assert "pip install" in str(exc_info.value) or "install" in str(exc_info.value).lower()


class TestParameterValidation:
    """Test input validation for scipy effects."""

    def test_band_pass_invalid_frequency_order(self):
        """low_cutoff must be less than high_cutoff."""

        seg = Sine(440).to_audio_segment(duration=100)

        with pytest.raises(ValueError, match="low_cutoff.*less than.*high_cutoff"):
            seg.band_pass_filter(2000, 1000)  # low > high

    def test_band_pass_frequency_exceeds_nyquist(self):
        """Cutoff frequency must be below Nyquist frequency."""

        seg = Sine(440).to_audio_segment(duration=100)  # 44100 Hz sample rate
        nyquist = seg.frame_rate / 2  # 22050 Hz

        with pytest.raises(ValueError, match="[Nn]yquist"):
            seg.band_pass_filter(100, nyquist + 1000)

    def test_high_pass_frequency_exceeds_nyquist(self):
        """High pass cutoff must be below Nyquist."""

        seg = Sine(440).to_audio_segment(duration=100)

        with pytest.raises(ValueError, match="[Nn]yquist"):
            seg.high_pass_filter(30000)  # > 22050 Hz

    def test_low_pass_frequency_exceeds_nyquist(self):
        """Low pass cutoff must be below Nyquist."""

        seg = Sine(440).to_audio_segment(duration=100)

        with pytest.raises(ValueError, match="[Nn]yquist"):
            seg.low_pass_filter(30000)

    def test_filter_order_must_be_positive(self):
        """Filter order must be a positive integer."""

        seg = Sine(440).to_audio_segment(duration=100)

        with pytest.raises(ValueError, match="order"):
            seg.high_pass_filter(1000, order=0)

        with pytest.raises(ValueError, match="order"):
            seg.high_pass_filter(1000, order=-1)


class TestBandPassFilter:
    """Tests for band_pass_filter effect."""

    def test_band_pass_preserves_in_band_frequency(self):
        """Frequency within passband should be preserved."""

        # 1kHz sine wave
        seg = Sine(1000).to_audio_segment(duration=500)
        # Band pass 500-1500 Hz (includes 1kHz)
        filtered = seg.band_pass_filter(500, 1500)

        # Should preserve most of the signal
        assert filtered.dBFS >= seg.dBFS - 3  # Within 3dB

    def test_band_pass_attenuates_out_of_band(self):
        """Frequency outside passband should be attenuated."""

        # 100Hz sine wave
        seg = Sine(100).to_audio_segment(duration=500)
        # Band pass 500-1500 Hz (excludes 100Hz)
        filtered = seg.band_pass_filter(500, 1500, order=5)

        # Should significantly attenuate
        assert filtered.dBFS < seg.dBFS - 20  # At least 20dB reduction

    def test_higher_order_steeper_rolloff(self):
        """Higher filter order should produce steeper rolloff."""

        seg = Sine(200).to_audio_segment(duration=500)

        filtered_order2 = seg.band_pass_filter(500, 1500, order=2)
        filtered_order5 = seg.band_pass_filter(500, 1500, order=5)

        # Order 5 should attenuate more than order 2
        assert filtered_order5.dBFS < filtered_order2.dBFS


class TestHighPassFilterScipy:
    """Tests for scipy high_pass_filter."""

    def test_high_pass_attenuates_low_frequency(self):
        """Low frequencies should be attenuated."""

        seg = Sine(100).to_audio_segment(duration=500)
        filtered = seg.high_pass_filter(500, order=5)

        assert filtered.dBFS < seg.dBFS - 15

    def test_high_pass_preserves_high_frequency(self):
        """High frequencies should pass through."""

        seg = Sine(2000).to_audio_segment(duration=500)
        filtered = seg.high_pass_filter(500, order=5)

        assert filtered.dBFS >= seg.dBFS - 3


class TestLowPassFilterScipy:
    """Tests for scipy low_pass_filter."""

    def test_low_pass_attenuates_high_frequency(self):
        """High frequencies should be attenuated."""

        seg = Sine(5000).to_audio_segment(duration=500)
        filtered = seg.low_pass_filter(1000, order=5)

        assert filtered.dBFS < seg.dBFS - 15

    def test_low_pass_preserves_low_frequency(self):
        """Low frequencies should pass through."""

        seg = Sine(200).to_audio_segment(duration=500)
        filtered = seg.low_pass_filter(1000, order=5)

        assert filtered.dBFS >= seg.dBFS - 3


class TestEq:
    """Tests for parametric EQ effect."""

    def test_invalid_filter_mode_raises_error(self):
        """Invalid filter mode should raise ValueError."""

        seg = Sine(440).to_audio_segment(duration=100)

        with pytest.raises(ValueError, match="[Mm]ode"):
            seg.eq(1000, filter_mode="invalid_mode")

    def test_invalid_channel_mode_raises_error(self):
        """Invalid channel mode should raise ValueError."""

        seg = Sine(440).to_audio_segment(duration=100)

        with pytest.raises(ValueError, match="[Cc]hannel"):
            seg.eq(1000, channel_mode="invalid")

    @pytest.mark.parametrize("mode", ["peak", "low_shelf", "high_shelf"])
    def test_eq_filter_modes_work(self, mode):
        """All filter modes should execute without error."""

        seg = Sine(440).to_audio_segment(duration=100)

        result = seg.eq(1000, filter_mode=mode, gain_dB=3)
        assert result is not None
        assert len(result) == len(seg)

    @pytest.mark.parametrize("channel_mode", ["L+R", "L", "R", "M+S", "M", "S"])
    def test_eq_channel_modes_work(self, channel_mode):
        """All channel modes should work on stereo audio."""

        seg = Sine(440).to_audio_segment(duration=100).set_channels(2)

        result = seg.eq(1000, channel_mode=channel_mode, gain_dB=3)
        assert result is not None
        assert result.channels == 2

    def test_eq_positive_gain_increases_level(self):
        """Positive gain should increase signal level at focus frequency."""

        seg = Sine(1000).to_audio_segment(duration=500)

        boosted = seg.eq(1000, bandwidth=200, gain_dB=6, filter_mode="peak")

        # Should be louder (allowing for implementation variance)
        assert boosted.dBFS > seg.dBFS

    def test_eq_negative_gain_decreases_level(self):
        """Negative gain should decrease signal level at focus frequency."""

        seg = Sine(1000).to_audio_segment(duration=500)

        cut = seg.eq(1000, bandwidth=200, gain_dB=-6, filter_mode="peak")

        # Should be quieter
        assert cut.dBFS < seg.dBFS

    def test_eq_mono_segment(self):
        """EQ should work on mono segments."""

        seg = Sine(440).to_audio_segment(duration=100).set_channels(1)

        result = seg.eq(1000, gain_dB=3)
        assert result.channels == 1
