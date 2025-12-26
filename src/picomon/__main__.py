"""Allow running picomon as a module."""

from .monitor import run
import sys

sys.exit(run())
