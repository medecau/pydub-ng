# These imports are needed to register effects with AudioSegment
from importlib.metadata import version

import pydub.effects as _  # noqa: F401

# Auto-import scipy effects if scipy is available
try:
    import pydub.scipy_effects as _  # noqa: F401

    _SCIPY_AVAILABLE = True
except ImportError:
    _SCIPY_AVAILABLE = False

from .audio_segment import AudioSegment

# Add introspection for scipy filter availability
AudioSegment.has_scipy_filters = _SCIPY_AVAILABLE

__version__ = version("pydub-ng")

__all__ = ["AudioSegment"]
