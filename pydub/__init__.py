# These imports are needed to register effects with AudioSegment
import pydub.effects as _  # noqa: F401

from .audio_segment import AudioSegment

__version__ = "0.25.1"
__all__ = ["AudioSegment"]
