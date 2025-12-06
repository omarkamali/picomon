from __future__ import annotations

try:
    from importlib import metadata as _metadata
except ImportError:  # pragma: no cover
    _metadata = None  # type: ignore[assignment]

from .config import PicomonConfig
from .monitor import run as run_monitor

__all__ = ["PicomonConfig", "run_monitor", "__version__"]

if _metadata is not None:
    try:  # pragma: no cover - best effort in editable installs
        __version__ = _metadata.version("picomon")
    except _metadata.PackageNotFoundError:  # type: ignore[attr-defined]
        __version__ = "0.0.0"
else:  # pragma: no cover
    __version__ = "0.0.0"
