import os
import sys
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if SRC_PATH.exists():
    sys.path.insert(0, str(SRC_PATH))
