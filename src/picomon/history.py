from __future__ import annotations

from collections import deque
from datetime import datetime
from typing import Deque

__all__ = ["GPUHistory", "parse_value_unit"]


def parse_value_unit(value) -> float:
    """Parse amd-smi outputs like {'value': 42, 'unit': '%'} into floats."""

    if isinstance(value, dict) and "value" in value:
        try:
            return float(value["value"])
        except (TypeError, ValueError):
            return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        stripped = str(value).strip().rstrip("%WMGBs/")
        return float(stripped)
    except (TypeError, ValueError):
        return 0.0


class GPUHistory:
    """Static info + rolling metric history for one GPU."""

    def __init__(self, max_points: int):
        self.hip_id: int | None = None
        self.vram_total_mb: float = 0.0
        self.power_limit_w: float = 0.0

        self.timestamps: Deque[datetime] = deque(maxlen=max_points)
        self.gfx: Deque[float] = deque(maxlen=max_points)
        self.umc: Deque[float] = deque(maxlen=max_points)
        self.power_w: Deque[float] = deque(maxlen=max_points)
        self.vram_used_mb: Deque[float] = deque(maxlen=max_points)

    def add_sample(
        self,
        ts: datetime,
        gfx: float,
        umc: float,
        power_w: float,
        vram_used_mb: float,
    ) -> None:
        self.timestamps.append(ts)
        self.gfx.append(gfx)
        self.umc.append(umc)
        self.power_w.append(power_w)
        self.vram_used_mb.append(vram_used_mb)

    def prune_before(self, cutoff: datetime) -> None:
        while self.timestamps and self.timestamps[0] < cutoff:
            self.timestamps.popleft()
            self.gfx.popleft()
            self.umc.popleft()
            self.power_w.popleft()
            self.vram_used_mb.popleft()

