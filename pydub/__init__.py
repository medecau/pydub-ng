# These imports are needed to register effects with AudioSegment
from importlib.metadata import version

import pydub.effects as _  # noqa: F401

from .audio_segment import AudioSegment

__version__ = version("pydub-ng")

__all__ = ["AudioSegment"]
