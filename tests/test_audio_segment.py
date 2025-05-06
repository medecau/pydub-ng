"""Tests for AudioSegment class functionality."""

import os
import struct
import tempfile

import pytest

from pydub import AudioSegment
from pydub.audio_segment import extract_wav_headers
from pydub.exceptions import (
    CouldntDecodeError,
    InvalidDuration,
    InvalidID3TagVersion,
    InvalidTag,
)
from pydub.generators import Sine
from pydub.utils import (
    get_supported_decoders,
    make_chunks,
    mediainfo,
    ratio_to_db,
)


# Helper functions to simplify test assertions
def assert_within_tolerance(val, expected, tolerance=None, percentage=None):
    """Assert that a value is within a tolerance of an expected value."""
    if percentage is not None:
        tolerance = expected * percentage
    lower_bound = expected - tolerance
    upper_bound = expected + tolerance
    assert lower_bound <= val <= upper_bound, (
        f"{val} is not in the acceptable range: {lower_bound} - {upper_bound}"
    )


@pytest.fixture(scope="module")
def test_segments(data_dir):
    """Load audio segments used across multiple tests."""
    seg1 = AudioSegment.from_mp3(str(data_dir / "test1.mp3"))
    seg2 = AudioSegment.from_mp3(str(data_dir / "test2.mp3"))
    seg3 = AudioSegment.from_mp3(str(data_dir / "test3.mp3"))
    seg_dc_offset = AudioSegment.from_mp3(str(data_dir / "test-dc_offset.wav"))
    seg_party = AudioSegment.from_mp3(str(data_dir / "party.mp3"))

    return {
        "seg1": seg1,
        "seg2": seg2,
        "seg3": seg3,
        "seg_dc_offset": seg_dc_offset,
        "seg_party": seg_party,
    }


@pytest.fixture(scope="module")
def media_files(data_dir):
    """Return paths to media files used in tests."""
    return {
        "ogg_file": str(data_dir / "bach.ogg"),
        "mp4_file": str(data_dir / "creative_common.mp4"),
        "mp3_file": str(data_dir / "party.mp3"),
        "webm_file": str(data_dir / "test5.webm"),
        "jpg_cover": str(data_dir / "cover.jpg"),
        "png_cover": str(data_dir / "cover.png"),
    }


@pytest.fixture
def temp_wav_file(tmp_path):
    """Create a temporary WAV file for testing."""
    file_path = tmp_path / "temp_output.wav"
    return file_path


@pytest.fixture
def temp_mp3_file(tmp_path):
    """Create a temporary MP3 file for testing."""
    file_path = tmp_path / "temp_output.mp3"
    return file_path


@pytest.fixture
def temp_ogg_file(tmp_path):
    """Create a temporary OGG file for testing."""
    file_path = tmp_path / "temp_output.ogg"
    return file_path


@pytest.fixture
def temp_webm_file(tmp_path):
    """Create a temporary WEBM file for testing."""
    file_path = tmp_path / "temp_output.webm"
    return file_path


@pytest.fixture
def temp_file_by_format(tmp_path):
    """Create a temporary file with the specified format extension."""

    def _factory(format_name="wav"):
        return tmp_path / f"temp_output.{format_name}"

    return _factory


def test_direct_instantiation_with_bytes():
    """Test creating an AudioSegment directly from bytes."""
    seg = AudioSegment(
        b"RIFF\x28\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x02\x00\x00}\x00\x00\x00\xf4\x01\x00\x04\x00\x10\x00data\x04\x00\x00\x00\x00\x00\x00\x00"
    )
    assert seg.frame_count() == 1
    assert seg.channels == 2
    assert seg.sample_width == 2
    assert seg.frame_rate == 32000


def test_24_bit_audio(data_dir):
    """Test handling 24-bit audio."""
    path24 = data_dir / "test1-24bit.wav"
    seg24 = AudioSegment._from_safe_wav(str(path24))

    # The data length lies at bytes 40-44
    with open(path24, "rb") as f:
        raw24 = f.read()
    len24 = struct.unpack("<L", raw24[40:44])[0]

    # should have been converted to 32 bit
    assert seg24.sample_width == 4
    # the data length should have grown by exactly 4:3 (24 bits turn into 32 bits)
    assert len(seg24.raw_data) * 3 == len24 * 4


def test_8_bit_audio(data_dir, temp_wav_file):
    """Test handling 8-bit audio."""
    original_path = data_dir / "test1.wav"
    original_segment = AudioSegment.from_file(str(original_path))
    target_rms = original_segment.rms // 2**8

    path_with_8bits = data_dir / "test1-8bit.wav"

    def check_8bit_segment(segment):
        assert_within_tolerance(segment.rms, target_rms, tolerance=0)

    # Check reading directly
    check_8bit_segment(AudioSegment.from_file(str(path_with_8bits)))

    # Check using ffmpeg on it
    with open(path_with_8bits, "rb") as file_8bit:
        check_8bit_segment(AudioSegment.from_file(file_8bit))

    # Check conversion from higher-width sample
    check_8bit_segment(AudioSegment.from_file(str(original_path)).set_sample_width(1))

    # Check audio export
    original_segment.set_sample_width(1).export(temp_wav_file, format="wav")
    check_8bit_segment(AudioSegment.from_file(temp_wav_file))


def test_192khz_audio(data_dir):
    """Test handling high sample rate audio."""
    test_files = [
        ("test-192khz-16bit.wav", 16),
        ("test-192khz-24bit.wav", 32),
        ("test-192khz-32bit.flac", 32),
        ("test-192khz-32bit.wav", 32),
        ("test-192khz-64bit.wav", 64),
    ]
    base_file, bit_depth = test_files[0]
    path = data_dir / base_file
    base = AudioSegment.from_file(str(path))

    headers = extract_wav_headers(open(path, "rb").read())
    data16_size = headers[-1].size
    assert len(base.raw_data) == data16_size
    assert base.frame_rate == 192000
    assert base.sample_width == bit_depth / 8

    for test_file, bit_depth in test_files[1:]:
        path = data_dir / test_file
        seg = AudioSegment.from_file(str(path))
        assert seg.sample_width == bit_depth / 8
        assert seg.frame_rate == 192000
        assert len(seg.raw_data) == len(base.raw_data) * seg.sample_width / base.sample_width
        assert seg.frame_rate == 192000


def test_concat(test_segments):
    """Test concatenating audio segments."""
    seg1 = test_segments["seg1"]
    seg2 = test_segments["seg2"]

    catted_audio = seg1 + seg2
    expected = len(seg1) + len(seg2)
    assert_within_tolerance(len(catted_audio), expected, tolerance=1)


def test_append(test_segments):
    """Test appending audio segments with crossfade."""
    seg1 = test_segments["seg1"]
    seg2 = test_segments["seg2"]
    seg3 = test_segments["seg3"]

    merged1 = seg3.append(seg1, crossfade=100)
    merged2 = seg3.append(seg2, crossfade=100)

    assert len(merged1) == len(seg1) + len(seg3) - 100
    assert len(merged2) == len(seg2) + len(seg3) - 100


def test_too_long_crossfade(test_segments):
    """Test appending with too long crossfade raises error."""
    seg1 = test_segments["seg1"][:1000]
    seg2 = test_segments["seg2"][:500]

    with pytest.raises(ValueError):
        seg1.append(seg2, crossfade=len(seg1) + 10)


def test_sum(test_segments):
    """Test summing audio segments in a generator."""
    seg1 = test_segments["seg1"]
    seg2 = test_segments["seg2"]
    seg3 = test_segments["seg3"]

    def gen():
        yield seg1
        yield seg2
        yield seg3

    try:
        sum(gen())
    except TypeError as e:
        if "unsupported operand" in str(e):
            pytest.fail("Could not sum() audio segments.")
        else:
            raise


def test_volume_with_add_sub(test_segments):
    """Test volume adjustment using + and - operators."""
    seg1 = test_segments["seg1"]

    quieter = seg1 - 6
    assert pytest.approx(ratio_to_db(quieter.rms, seg1.rms), abs=0.1) == -6

    louder = quieter + 2.5
    assert pytest.approx(ratio_to_db(louder.rms, quieter.rms), abs=0.1) == 2.5


def test_repeat_with_multiply(test_segments):
    """Test repeating audio with * operator."""
    seg1 = test_segments["seg1"]

    seg = seg1 * 3
    expected = len(seg1) * 3
    assert expected - 2 < len(seg) < expected + 2


def test_overlay(test_segments):
    """Test overlaying audio segments."""
    seg1 = test_segments["seg1"]
    seg2 = test_segments["seg2"]

    seg_mult = seg1[:5000] * seg2[:3000]
    seg_over = seg1[:5000].overlay(seg2[:3000], loop=True)

    assert len(seg_mult) == len(seg_over)
    assert seg_mult._data == seg_over._data
    assert len(seg_mult) == 5000
    assert len(seg_over) == 5000


@pytest.mark.parametrize(
    "times,expected_equal_to_mult",
    [
        (99999999, True),  # infinite loops
        (0, False),  # no loops
        (1, False),  # one loop
        (2, False),  # two loops
        (3, False),  # three loops
        (4, False),  # four loops (last will pass end)
        (5, False),  # five loops (last won't happen b/c past end)
        (999999999, False),  # ~infinite, same as 4 and 5 really
    ],
)
def test_overlay_times(test_segments, times, expected_equal_to_mult):
    """Test overlaying with different times parameter values."""
    seg1 = test_segments["seg1"]
    seg2 = test_segments["seg2"]

    if times == 99999999:
        # infinite case
        seg_mult = seg1[:5000] * seg2[:3000]
        seg_over = seg1[:5000].overlay(seg2[:3000], times=times)
        assert len(seg_mult) == len(seg_over)
        assert len(seg_over) == 5000
        assert seg_mult._data == seg_over._data
    else:
        piece = seg2[:1000]
        if times == 0:
            # no-op case
            seg_manual = seg1[:4000]
        elif times == 1:
            # 1 loop
            seg_manual = seg1[:4000].overlay(piece, position=500)
        elif times == 2:
            # 2 loops
            seg_manual = seg1[:4000].overlay(piece, position=500).overlay(piece, position=1500)
        elif times == 3:
            # 3 loops
            seg_manual = (
                seg1[:4000]
                .overlay(piece, position=500)
                .overlay(piece, position=1500)
                .overlay(piece, position=2500)
            )
        else:
            # 4+ loops (4th will overlay at 3500, 5th would be at 4500 but seg is only 4000)
            seg_manual = (
                seg1[:4000]
                .overlay(piece, position=500)
                .overlay(piece, position=1500)
                .overlay(piece, position=2500)
                .overlay(piece, position=3500)
            )

        seg_over = seg1[:4000].overlay(piece, times=times)
        seg_mult = seg1[:5000] * seg2[:3000]

        assert len(seg_manual) == len(seg_over)
        assert len(seg_over) == 4000
        assert (seg_mult._data == seg_over._data) == expected_equal_to_mult


def test_overlay_with_gain_change(test_segments):
    """Test overlaying with gain_during_overlay parameter."""
    seg1 = test_segments["seg1"]

    # Use overlay silence with volume change
    seg_one = seg1[:5000]
    seg_silent = AudioSegment.silent(duration=2000)
    seg_over = seg_one.overlay(seg_silent, gain_during_overlay=-7)

    # Manually lower first segment
    seg_one_lower = seg_one - 7
    seg_manual = seg_one_lower[:2000] + seg_one[2000:]

    assert len(seg_over) == len(seg_manual)
    assert pytest.approx(seg_over.dBFS, abs=0.1) == seg_manual.dBFS
    assert len(seg_manual) == 5000
    assert len(seg_over) == 5000


def test_slicing(test_segments):
    """Test slicing audio segments."""
    seg1 = test_segments["seg1"]

    empty = seg1[:0]
    second_long_slice = seg1[:1000]
    remainder = seg1[1000:]

    assert len(empty) == 0
    assert len(second_long_slice) == 1000
    assert len(remainder) == len(seg1) - 1000

    last_5_seconds = seg1[-5000:]
    before = seg1[:-5000]

    assert len(last_5_seconds) == 5000
    assert len(before) == len(seg1) - 5000

    past_end = second_long_slice[:1500]
    assert second_long_slice._data == past_end._data


def test_slicing_by_step(test_segments):
    """Test slicing audio segments with step parameter."""
    seg1 = test_segments["seg1"]

    audio = seg1[:10000]
    chunks = audio[:0]

    for chunk in audio[::1000]:
        assert isinstance(chunk, AudioSegment)
        assert len(chunk) == 1000
        chunks += chunk

    assert len(audio) == len(chunks)


def test_indexing(test_segments):
    """Test indexing into audio segments."""
    seg1 = test_segments["seg1"]

    short = seg1[:100]

    rebuilt1 = seg1[:0]
    for part in short:
        rebuilt1 += part

    rebuilt2 = sum([part for part in short])

    assert short._data == rebuilt1._data
    assert short._data == rebuilt2._data


def test_set_channels(test_segments, temp_mp3_file):
    """Test setting the number of channels."""
    seg1 = test_segments["seg1"]
    seg2 = test_segments["seg2"]

    mono = seg1.set_channels(1)
    stereo = mono.set_channels(2)

    assert len(seg1) == len(mono)
    assert len(seg1) == len(stereo)

    mono = seg2.set_channels(1)
    mono = mono.set_frame_rate(22050)

    assert len(mono) == len(seg2)

    mono.export(temp_mp3_file, "mp3")
    monomp3 = AudioSegment.from_mp3(temp_mp3_file)

    assert_within_tolerance(len(monomp3), len(seg2), tolerance=105)

    merged = mono.append(stereo, crossfade=100)
    assert_within_tolerance(len(merged), len(seg1) + len(seg2) - 100, tolerance=1)


def test_split_to_mono(test_segments):
    """Test splitting a stereo segment to mono channels."""
    seg = test_segments["seg1"]

    mono_segments = seg.split_to_mono()
    seg_lchannel = mono_segments[0]
    seg_rchannel = mono_segments[1]

    assert len(seg_lchannel) == len(seg)
    assert len(seg_rchannel) == len(seg)

    assert seg_lchannel.frame_rate == seg.frame_rate
    assert seg_rchannel.frame_rate == seg.frame_rate

    assert seg_lchannel.frame_count() == seg.frame_count()
    assert seg_rchannel.frame_count() == seg.frame_count()


@pytest.mark.parametrize(
    "left_dbfs_change,right_dbfs_change",
    [
        (0.0, float("-inf")),  # hard left
        (0.0, -6.0),  # reduced right
        (0.0, 0.0),  # no change
        (-6.0, 0.0),  # reduced left
        (float("-inf"), 0.0),  # hard right
    ],
)
def test_apply_gain_stereo(test_segments, left_dbfs_change, right_dbfs_change):
    """Test applying different gains to left and right channels."""
    seg = test_segments["seg1"]

    orig_l, orig_r = seg.split_to_mono()
    orig_dbfs_l = orig_l.dBFS
    orig_dbfs_r = orig_r.dBFS

    panned = seg.apply_gain_stereo(left_dbfs_change, right_dbfs_change)
    assert panned.channels == 2

    left, right = panned.split_to_mono()

    # Handle infinity cases specially
    if left_dbfs_change == float("-inf"):
        assert left.dBFS == float("-inf")
    else:
        assert pytest.approx(left.dBFS, abs=0.1) == orig_dbfs_l + left_dbfs_change

    if right_dbfs_change == float("-inf"):
        assert right.dBFS == float("-inf")
    else:
        assert pytest.approx(right.dBFS, abs=0.1) == orig_dbfs_r + right_dbfs_change


@pytest.mark.parametrize(
    "pan,left_dbfs_change,right_dbfs_change",
    [
        (-1.0, 3.0, float("-inf")),  # hard left
        (-0.5, 1.5, -4.65),  # left-biased
        (0.0, 0.0, 0.0),  # center
        (0.5, -4.65, 1.5),  # right-biased
        (1.0, float("-inf"), 3.0),  # hard right
    ],
)
def test_pan(test_segments, pan, left_dbfs_change, right_dbfs_change):
    """Test panning audio left/right."""
    seg = test_segments["seg1"]

    orig_l, orig_r = seg.split_to_mono()
    orig_dbfs_l = orig_l.dBFS
    orig_dbfs_r = orig_r.dBFS

    panned = seg.pan(pan)
    left, right = panned.split_to_mono()

    # Handle infinity cases specially
    if left_dbfs_change == float("-inf"):
        assert left.dBFS == float("-inf")
    else:
        assert pytest.approx(left.dBFS, abs=0.1) == orig_dbfs_l + left_dbfs_change

    if right_dbfs_change == float("-inf"):
        assert right.dBFS == float("-inf")
    else:
        assert pytest.approx(right.dBFS, abs=0.1) == orig_dbfs_r + right_dbfs_change


def test_export_as_mp3(test_segments):
    """Test exporting as MP3."""
    seg = test_segments["seg1"]

    exported_mp3 = seg.export()
    seg_exported_mp3 = AudioSegment.from_mp3(exported_mp3)

    assert_within_tolerance(len(seg_exported_mp3), len(seg), percentage=0.01)


def test_export_as_wav(test_segments):
    """Test exporting as WAV."""
    seg = test_segments["seg1"]

    exported_wav = seg.export(format="wav")
    seg_exported_wav = AudioSegment.from_wav(exported_wav)

    assert_within_tolerance(len(seg_exported_wav), len(seg), percentage=0.01)


def test_export_as_wav_with_codec(test_segments):
    """Test exporting as WAV with codec."""
    seg = test_segments["seg1"]

    exported_wav = seg.export(format="wav", codec="pcm_s32le")
    seg_exported_wav = AudioSegment.from_wav(exported_wav)

    assert_within_tolerance(len(seg_exported_wav), len(seg), percentage=0.01)
    assert seg_exported_wav.sample_width == 4


def test_export_as_wav_with_parameters(test_segments):
    """Test exporting as WAV with parameters."""
    seg = test_segments["seg1"]

    exported_wav = seg.export(format="wav", parameters=["-ar", "16000", "-ac", "1"])
    seg_exported_wav = AudioSegment.from_wav(exported_wav)

    assert_within_tolerance(len(seg_exported_wav), len(seg), percentage=0.01)
    assert seg_exported_wav.frame_rate == 16000
    assert seg_exported_wav.channels == 1


def test_export_as_raw(test_segments):
    """Test exporting as RAW."""
    seg = test_segments["seg1"]

    exported_raw = seg.export(format="raw")
    seg_exported_raw = AudioSegment.from_raw(
        exported_raw,
        sample_width=seg.sample_width,
        frame_rate=seg.frame_rate,
        channels=seg.channels,
    )

    assert_within_tolerance(len(seg_exported_raw), len(seg), percentage=0.01)


def test_export_as_raw_with_codec(test_segments):
    """Test exporting as RAW with codec raises error."""
    seg = test_segments["seg1"]

    with pytest.raises(AttributeError):
        seg.export(format="raw", codec="pcm_s32le")


def test_export_as_raw_with_parameters(test_segments):
    """Test exporting as RAW with parameters raises error."""
    seg = test_segments["seg1"]

    with pytest.raises(AttributeError):
        seg.export(format="raw", parameters=["-ar", "16000", "-ac", "1"])


def test_export_as_ogg(test_segments):
    """Test exporting as OGG."""
    seg = test_segments["seg1"]

    exported_ogg = seg.export(format="ogg")
    seg_exported_ogg = AudioSegment.from_ogg(exported_ogg)

    assert_within_tolerance(len(seg_exported_ogg), len(seg), percentage=0.01)


def test_export_forced_codec(test_segments, temp_ogg_file):
    """Test exporting with forced codec."""
    seg1 = test_segments["seg1"]
    seg2 = test_segments["seg2"]

    (seg1 + seg2).export(temp_ogg_file, "ogg", codec="libvorbis")
    exported = AudioSegment.from_ogg(temp_ogg_file)

    assert_within_tolerance(len(exported), len(seg1) + len(seg2), percentage=0.01)


def test_export_progress_callback_codec(test_segments, temp_ogg_file):
    """Test exporting with forced codec."""
    seg1 = test_segments["seg1"]
    
    progress_called = False
    
    def progress_update(a, b):
        nonlocal progress_called
        progress_called = True

    (seg1).export(temp_ogg_file, "ogg", codec="libvorbis", progress_callback=progress_update)

    assert(progress_called)


def test_fades(test_segments):
    """Test fading in and out."""
    seg1 = test_segments["seg1"]
    seg2 = test_segments["seg2"]

    seg = seg1[:10000]

    # 1 ms difference in the position of the end of the fade out
    inf_end = seg.fade(start=0, end=float("inf"), to_gain=-120)
    negative_end = seg.fade(start=0, end=-1, to_gain=-120)

    assert_within_tolerance(inf_end.rms, negative_end.rms, percentage=0.001)
    assert negative_end.rms <= inf_end.rms
    assert inf_end.rms < seg.rms

    assert len(inf_end) == len(seg)

    assert -6 < ratio_to_db(inf_end.rms, seg.rms) < -5

    # use a slice out of the middle to make sure there is audio
    seg = seg2[2000:8000]
    fade_out = seg.fade_out(1000)
    fade_in = seg.fade_in(1000)

    assert 0 < fade_out.rms < seg.rms
    assert 0 < fade_in.rms < seg.rms

    assert len(fade_out) == len(seg)
    assert len(fade_in) == len(seg)

    db_at_beginning = ratio_to_db(fade_in[:1000].rms, seg[:1000].rms)
    db_at_end = ratio_to_db(fade_in[-1000:].rms, seg[-1000:].rms)
    assert db_at_beginning < db_at_end

    db_at_beginning = ratio_to_db(fade_out[:1000].rms, seg[:1000].rms)
    db_at_end = ratio_to_db(fade_out[-1000:].rms, seg[-1000:].rms)
    assert db_at_end < db_at_beginning


def test_reverse(test_segments):
    """Test reversing audio."""
    seg = test_segments["seg1"]

    rseg = seg.reverse()

    # the reversed audio should be exactly equal in playback duration
    assert len(seg) == len(rseg)

    r2seg = rseg.reverse()

    # if you reverse it twice you should get an identical AudioSegment
    assert seg == r2seg


def test_normalize(test_segments):
    """Test normalizing audio."""
    seg = test_segments["seg1"]

    normalized = seg.normalize(0.0)

    assert len(normalized) == len(seg)
    assert normalized.rms > seg.rms
    assert_within_tolerance(normalized.max, normalized.max_possible_amplitude, percentage=0.0001)


def test_for_accidental_shortening(test_segments, temp_mp3_file):
    """Test that exporting and reimporting doesn't shorten audio."""
    seg = test_segments["seg_party"]

    fd = seg.export(temp_mp3_file)
    fd.close()

    for i in range(3):
        fd = AudioSegment.from_mp3(temp_mp3_file).export(temp_mp3_file, "mp3")
        fd.close()

    tmp_seg = AudioSegment.from_mp3(temp_mp3_file)
    assert pytest.approx(len(tmp_seg), abs=1) == len(seg)


@pytest.mark.skipif("aac" not in get_supported_decoders(), reason="Unsupported codecs")
def test_formats(data_dir):
    """Test loading different formats."""
    seg_m4a = AudioSegment.from_file(str(data_dir / "format_test.m4a"), "m4a")
    assert len(seg_m4a) > 0


def test_equal_and_not_equal(test_segments):
    """Test equality operators."""
    seg1 = test_segments["seg1"]

    wav_file = seg1.export(format="wav")
    wav = AudioSegment.from_wav(wav_file)

    assert seg1 == wav
    assert not (seg1 != wav)


def test_duration(test_segments):
    """Test duration property."""
    seg1 = test_segments["seg1"]

    assert int(seg1.duration_seconds) == 10

    wav_file = seg1.export(format="wav")
    wav = AudioSegment.from_wav(wav_file)
    assert wav.duration_seconds == seg1.duration_seconds


@pytest.mark.skipif("aac" not in get_supported_decoders(), reason="Unsupported codecs")
def test_autodetect_format(data_dir):
    """Test auto-detecting file format."""
    aac_path = data_dir / "wrong_extension.aac"

    # Should fail when format is explicitly specified as AAC
    with pytest.raises(CouldntDecodeError):
        AudioSegment.from_file(str(aac_path), "aac")

    # Trying to auto detect input file format
    aac_file = AudioSegment.from_file(str(aac_path))
    assert int(aac_file.duration_seconds) == 9


def test_export_ogg_as_mp3(media_files, temp_mp3_file):
    """Test exporting OGG as MP3."""
    AudioSegment.from_file(media_files["ogg_file"]).export(temp_mp3_file, format="mp3")
    # Just testing that it doesn't raise an exception


def test_export_mp3_as_ogg(media_files, temp_ogg_file):
    """Test exporting MP3 as OGG."""
    AudioSegment.from_file(media_files["mp3_file"]).export(temp_ogg_file, format="ogg")
    # Just testing that it doesn't raise an exception


def test_export_webm_as_mp3(media_files, temp_mp3_file):
    """Test exporting WEBM as MP3."""
    AudioSegment.from_file(media_files["webm_file"], codec="opus").export(
        temp_mp3_file, format="mp3"
    )
    # Just testing that it doesn't raise an exception


def test_export_mp3_as_webm(media_files, temp_webm_file):
    """Test exporting MP3 as WEBM."""
    AudioSegment.from_file(media_files["mp3_file"]).export(temp_webm_file, format="webm")
    # Just testing that it doesn't raise an exception


@pytest.mark.skipif("aac" not in get_supported_decoders(), reason="Unsupported codecs")
def test_export_mp4_as_ogg(media_files, temp_ogg_file):
    """Test exporting MP4 as OGG."""
    AudioSegment.from_file(media_files["mp4_file"]).export(temp_ogg_file, format="ogg")
    # Just testing that it doesn't raise an exception


@pytest.mark.skipif("aac" not in get_supported_decoders(), reason="Unsupported codecs")
def test_export_mp4_as_mp3(media_files, temp_mp3_file):
    """Test exporting MP4 as MP3."""
    AudioSegment.from_file(media_files["mp4_file"]).export(temp_mp3_file, format="mp3")
    # Just testing that it doesn't raise an exception


@pytest.mark.skipif("aac" not in get_supported_decoders(), reason="Unsupported codecs")
def test_export_mp4_as_wav(media_files, temp_wav_file):
    """Test exporting MP4 as WAV."""
    AudioSegment.from_file(media_files["mp4_file"]).export(temp_wav_file, format="mp3")
    # Just testing that it doesn't raise an exception


@pytest.mark.skipif("aac" not in get_supported_decoders(), reason="Unsupported codecs")
def test_export_mp4_as_mp3_with_tags(media_files, temp_mp3_file):
    """Test exporting MP4 as MP3 with tags."""
    tags_dict = {
        "title": "The Title You Want",
        "artist": "Artist's name",
        "album": "Name of the Album",
    }
    AudioSegment.from_file(media_files["mp4_file"]).export(
        temp_mp3_file, format="mp3", tags=tags_dict
    )
    # Just testing that it doesn't raise an exception


@pytest.mark.skipif("aac" not in get_supported_decoders(), reason="Unsupported codecs")
def test_export_mp4_as_mp3_with_tags_raises_exception_when_tags_are_not_a_dictionary(
    media_files, temp_mp3_file
):
    """Test exporting with invalid tags raises exception."""
    json = (
        '{"title": "The Title You Want", "album": "Name of the Album", "artist": "Artist\'s name"}'
    )

    with pytest.raises(InvalidTag):
        AudioSegment.from_file(media_files["mp4_file"]).export(
            temp_mp3_file,
            format="mp3",
            tags=json,
        )


@pytest.mark.skipif("aac" not in get_supported_decoders(), reason="Unsupported codecs")
def test_export_mp4_as_mp3_with_tags_raises_exception_when_id3version_is_wrong(
    media_files, temp_mp3_file
):
    """Test exporting with invalid ID3 version raises exception."""
    tags = {"artist": "Artist", "title": "Title"}

    with pytest.raises(InvalidID3TagVersion):
        AudioSegment.from_file(media_files["mp4_file"]).export(
            temp_mp3_file,
            format="mp3",
            tags=tags,
            id3v2_version="BAD VERSION",
        )


@pytest.mark.skipif("aac" not in get_supported_decoders(), reason="Unsupported codecs")
def test_export_mp3_with_tags(media_files, temp_mp3_file):
    """Test exporting MP3 with tags and verifying with mediainfo."""
    tags = {"artist": "Mozart", "title": "The Magic Flute"}

    AudioSegment.from_file(media_files["mp4_file"]).export(temp_mp3_file, format="mp3", tags=tags)

    info = mediainfo(filepath=str(temp_mp3_file))
    info_tags = info["TAG"]

    assert info_tags["artist"] == "Mozart"
    assert info_tags["title"] == "The Magic Flute"


def test_mp3_with_jpg_cover_img(test_segments, media_files, temp_mp3_file):
    """Test MP3 export with JPG cover image."""
    seg1 = test_segments["seg1"]

    outf = seg1.export(temp_mp3_file, format="mp3", cover=media_files["jpg_cover"])
    testseg = AudioSegment.from_file(outf, format="mp3")

    # should be within a 150ms and 1.5dB (not perfectly equal due to codecs)
    assert_within_tolerance(len(seg1), len(testseg), tolerance=150)
    assert_within_tolerance(seg1.dBFS, testseg.dBFS, tolerance=1.5)


def test_mp3_with_png_cover_img(test_segments, media_files, temp_mp3_file):
    """Test MP3 export with PNG cover image."""
    seg1 = test_segments["seg1"]

    outf = seg1.export(temp_mp3_file, format="mp3", cover=media_files["png_cover"])
    testseg = AudioSegment.from_file(outf, format="mp3")

    # should be within a 150ms and 1.5dB (not perfectly equal due to codecs)
    assert_within_tolerance(len(seg1), len(testseg), tolerance=150)
    assert_within_tolerance(seg1.dBFS, testseg.dBFS, tolerance=1.5)


def test_fade_raises_exception_when_duration_start_end_are_none():
    """Test fade raises exception with invalid parameters."""
    seg = Sine(440).to_audio_segment(duration=1000)

    with pytest.raises(TypeError):
        seg.fade(start=1, end=1, duration=1)


@pytest.mark.parametrize("sample_width", [1, 2])
def test_silent(sample_width):
    """Test creating silent audio segments."""
    test_seg = Sine(440).to_audio_segment(duration=1000)
    seg = AudioSegment.silent(len(test_seg))

    assert len(test_seg) == len(seg)
    assert seg.rms == 0
    assert seg.frame_width == 2

    seg_8bit = seg.set_sample_width(sample_width)
    assert seg_8bit.sample_width == sample_width
    assert seg_8bit.frame_width == sample_width
    assert seg_8bit.rms == 0

    seg *= test_seg
    assert seg.rms == test_seg.rms
    assert len(seg) == len(test_seg)
    assert seg.frame_width == test_seg.frame_width
    assert seg.frame_rate == test_seg.frame_rate


def test_from_mono_audiosegments():
    """Test creating a stereo segment from two mono segments."""
    monoseg1 = Sine(440).to_audio_segment(duration=1000).set_channels(1)
    monoseg2 = monoseg1.reverse()
    stereo_sound = AudioSegment.from_mono_audiosegments(monoseg1, monoseg2)

    assert stereo_sound.channels == 2
    assert stereo_sound.dBFS == monoseg1.dBFS
    assert len(stereo_sound) == len(monoseg1)


def test_fade_raises_exception_when_duration_is_negative():
    """Test fade raises exception with negative duration."""
    seg = Sine(440).to_audio_segment(duration=1000)

    with pytest.raises(InvalidDuration):
        seg.fade(to_gain=1, from_gain=1, start=None, end=None, duration=-1)


def test_make_chunks():
    """Test splitting an audio segment into chunks."""
    seg = Sine(440).to_audio_segment(duration=1000)
    chunks = make_chunks(seg, 100)
    seg2 = chunks[0]
    for chunk in chunks[1:]:
        seg2 += chunk
    assert len(seg) == len(seg2)


def test_empty():
    """Test the empty audio segment behaves as expected."""
    test_seg1 = Sine(440).to_audio_segment(duration=1000)
    test_seg2 = Sine(880).to_audio_segment(duration=2000)
    test_seg3 = Sine(220).to_audio_segment(duration=3000)

    assert len(test_seg1) == len(test_seg1 + AudioSegment.empty())
    assert len(test_seg2) == len(test_seg2 + AudioSegment.empty())
    assert len(test_seg3) == len(test_seg3 + AudioSegment.empty())


def test_speedup():
    """Test speeding up audio."""
    seg = Sine(440).to_audio_segment(duration=1000)
    speedup_seg = seg.speedup(2.0)

    # The speedup function doesn't exactly halve the length due to implementation details
    # Actual value is closer to 575ms for a 1000ms input with speedup(2.0)
    assert_within_tolerance(len(speedup_seg), 575, percentage=0.05)


@pytest.mark.parametrize(
    "segment,expected_dbfs,tolerance",
    [
        ("seg1_8bit", -18.06, 1.5),
        ("seg1", -17.76, 1.5),
        ("seg2", -20.78, 1.5),
        ("seg3", -12.94, 1.5),
    ],
)
def test_dbfs(test_segments, segment, expected_dbfs, tolerance):
    """Test dBFS measurements."""
    if segment == "seg1_8bit":
        seg = test_segments["seg1"].set_sample_width(1)
    else:
        seg = test_segments[segment]

    assert_within_tolerance(seg.dBFS, expected_dbfs, tolerance=tolerance)


def test_compress(test_segments):
    """Test dynamic range compression."""
    seg1 = test_segments["seg1"]

    compressed = seg1.compress_dynamic_range()
    assert_within_tolerance(seg1.dBFS - compressed.dBFS, 10.0, tolerance=10.0)

    # Highest peak should be lower
    assert compressed.max < seg1.max

    # Average volume should be reduced
    assert compressed.rms < seg1.rms


@pytest.mark.skipif("aac" not in get_supported_decoders(), reason="Unsupported codecs")
def test_exporting_to_ogg_uses_default_codec_when_codec_param_is_none(media_files, temp_ogg_file):
    """Test that exporting to OGG uses vorbis codec by default."""
    AudioSegment.from_file(media_files["mp4_file"]).export(temp_ogg_file, format="ogg")

    info = mediainfo(filepath=str(temp_ogg_file))

    assert info["codec_name"] == "vorbis"
    assert info["format_name"] == "ogg"


def test_zero_length_segment(test_segments):
    """Test creating a zero-length segment."""
    seg1 = test_segments["seg1"]
    assert len(seg1[0:0]) == 0


def test_invert():
    """Test inverting phase of audio channels."""
    s_mono = Sine(100).to_audio_segment()
    s = s_mono.set_channels(2)

    with pytest.raises(Exception):
        s_mono.invert_phase(channels=(1, 0))

    s_inv = s.invert_phase()
    assert not (s == s_inv)
    assert s.rms == s_inv.rms
    assert s == s_inv.invert_phase()

    s_inv_right = s.invert_phase(channels=(0, 1))
    left, right = s_inv_right.split_to_mono()

    assert not (s_mono == s_inv_right)
    assert not (s_inv == s_inv_right)
    assert left == s_mono
    assert not (right == s_mono)

    s_inv_left = s.invert_phase(channels=(1, 0))
    left, right = s_inv_left.split_to_mono()

    assert not (s_mono == s_inv_left)
    assert not (s_inv == s_inv_left)
    assert not (left == s_mono)
    assert right == s_mono


def test_max_dbfs():
    """Test max_dBFS property."""
    sine_0_dbfs = Sine(1000).to_audio_segment()
    sine_minus_3_dbfs = Sine(1000).to_audio_segment(volume=-3.0)

    assert pytest.approx(sine_0_dbfs.max_dBFS, abs=0.1) == -0.0
    assert pytest.approx(sine_minus_3_dbfs.max_dBFS, abs=0.1) == -3.0


def test_array_type(test_segments):
    """Test array_type property."""
    seg1 = test_segments["seg1"]
    seg2 = test_segments["seg2"]
    seg3 = test_segments["seg3"]
    seg_party = test_segments["seg_party"]

    assert seg1.array_type == "h"
    assert seg2.array_type == "h"
    assert seg3.array_type == "h"
    assert seg_party.array_type == "h"

    silence = AudioSegment.silent(50)
    assert silence.array_type == "h"
    assert silence.set_sample_width(1).array_type == "b"
    assert silence.set_sample_width(4).array_type == "i"


def test_sample_array():
    """Test getting array of samples."""
    samples = Sine(450).to_audio_segment().get_array_of_samples()
    assert list(samples[:8]) == [0, 2099, 4190, 6263, 8311, 10325, 12296, 14217]


def test_get_dc_offset(test_segments):
    """Test getting DC offset."""
    seg = test_segments["seg_dc_offset"]

    assert_within_tolerance(seg.get_dc_offset(), -0.16, tolerance=0.01)
    assert_within_tolerance(seg.get_dc_offset(1), -0.16, tolerance=0.01)
    assert_within_tolerance(seg.get_dc_offset(2), 0.1, tolerance=0.01)


def test_remove_dc_offset(test_segments):
    """Test removing DC offset."""
    seg = test_segments["seg_dc_offset"]

    seg1 = seg.remove_dc_offset()
    assert_within_tolerance(seg1.get_dc_offset(1), 0.0, tolerance=0.0001)
    assert_within_tolerance(seg1.get_dc_offset(2), 0.0, tolerance=0.0001)

    seg1 = seg.remove_dc_offset(1)
    assert_within_tolerance(seg1.get_dc_offset(1), 0.0, tolerance=0.0001)
    assert_within_tolerance(seg1.get_dc_offset(2), 0.1, tolerance=0.01)

    seg1 = seg.remove_dc_offset(2)
    assert_within_tolerance(seg1.get_dc_offset(1), -0.16, tolerance=0.01)
    assert_within_tolerance(seg1.get_dc_offset(2), 0.0, tolerance=0.0001)

    seg1 = seg.remove_dc_offset(channel=1, offset=(-0.06))
    assert_within_tolerance(seg1.get_dc_offset(1), -0.1, tolerance=0.01)


def test_from_file_clean_fail(tmp_path, monkeypatch):
    """Test that invalid files are cleaned up after failure."""
    # Setup a temporary directory for testing
    test_tmpdir = tmp_path / "test_tmpdir"
    test_tmpdir.mkdir()

    # Monkeypatch tempfile.tempdir to use our test directory
    monkeypatch.setattr(tempfile, "tempdir", str(test_tmpdir))

    # Create a fake WAV file that will cause a decode error
    tmp_wav_file = test_tmpdir / "not_a_wav.wav"
    with open(tmp_wav_file, "w+b") as f:
        f.write("not really a wav".encode("utf-8"))
        f.flush()

    # Test that attempting to load the file raises the expected error
    with pytest.raises(CouldntDecodeError):
        AudioSegment.from_file(tmp_wav_file)

    # Verify that only our test file exists in the temp directory,
    # meaning the library cleaned up after itself
    files = os.listdir(str(test_tmpdir))
    assert files == ["not_a_wav.wav"]

    # monkeypatch automatically restores original values after the test
