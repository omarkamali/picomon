from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PicomonConfig:
    """Runtime configuration for picomon."""

    update_interval: float = 3.0
    history_minutes: int = 30
    static_timeout: float = 10.0
    metric_timeout: float = 5.0

    def __post_init__(self) -> None:
        if self.update_interval <= 0:
            raise ValueError("update_interval must be greater than zero")
        if self.history_minutes <= 0:
            raise ValueError("history_minutes must be greater than zero")
        if self.static_timeout <= 0:
            raise ValueError("static_timeout must be greater than zero")
        if self.metric_timeout <= 0:
            raise ValueError("metric_timeout must be greater than zero")

    @property
    def max_points(self) -> int:
        """Maximum number of samples to retain per metric."""

        return max(1, int(self.history_minutes * 60 / self.update_interval))
