"""Base provider interface for GPU metrics collection."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
from typing import Deque, Dict, List, Optional


@dataclass
class GPUStaticInfo:
    """Static information about a GPU that doesn't change."""

    # Identity
    gpu_idx: int
    name: str = "Unknown GPU"
    vendor: str = "Unknown"

    # Hardware info
    architecture: str = ""
    compute_units: int = 0
    pcie_bus: str = ""

    # Capabilities
    vram_total_mb: float = 0.0
    power_limit_w: float = 0.0

    # Ordering hint (e.g., HIP ID for AMD)
    sort_index: int | None = None


@dataclass
class GPUMetrics:
    """Current metrics snapshot for a GPU."""

    timestamp: datetime
    gpu_idx: int

    # Utilization (0-100%)
    gpu_utilization: float = 0.0  # Graphics/compute utilization
    memory_controller_utilization: float = 0.0  # Memory controller activity

    # Power (watts)
    power_draw_w: float = 0.0

    # Memory (MB)
    vram_used_mb: float = 0.0

    # Temperature (Celsius) - optional
    temperature_c: float | None = None

    # Clock speeds (MHz) - optional
    gpu_clock_mhz: int | None = None
    memory_clock_mhz: int | None = None

    # Fan speed (%) - optional
    fan_speed_percent: float | None = None


@dataclass
class GPUHistory:
    """Historical metrics for a GPU with rolling window."""

    static_info: GPUStaticInfo
    max_points: int = 600

    # History deques
    timestamps: Deque[datetime] = field(default_factory=deque)
    gpu_util: Deque[float] = field(default_factory=deque)
    mem_ctrl_util: Deque[float] = field(default_factory=deque)
    power_w: Deque[float] = field(default_factory=deque)
    vram_used_mb: Deque[float] = field(default_factory=deque)
    temperature_c: Deque[float] = field(default_factory=deque)

    def __post_init__(self):
        """Initialize deques with max length."""
        self.timestamps = deque(maxlen=self.max_points)
        self.gpu_util = deque(maxlen=self.max_points)
        self.mem_ctrl_util = deque(maxlen=self.max_points)
        self.power_w = deque(maxlen=self.max_points)
        self.vram_used_mb = deque(maxlen=self.max_points)
        self.temperature_c = deque(maxlen=self.max_points)

    def add_metrics(self, metrics: GPUMetrics) -> None:
        """Add a metrics snapshot to history."""
        self.timestamps.append(metrics.timestamp)
        self.gpu_util.append(metrics.gpu_utilization)
        self.mem_ctrl_util.append(metrics.memory_controller_utilization)
        self.power_w.append(metrics.power_draw_w)
        self.vram_used_mb.append(metrics.vram_used_mb)
        if metrics.temperature_c is not None:
            self.temperature_c.append(metrics.temperature_c)

    # Convenience properties for backwards compatibility
    @property
    def gpu_idx(self) -> int:
        return self.static_info.gpu_idx

    @property
    def name(self) -> str:
        return self.static_info.name

    @property
    def vendor(self) -> str:
        return self.static_info.vendor

    @property
    def vram_total_mb(self) -> float:
        return self.static_info.vram_total_mb

    @property
    def power_limit_w(self) -> float:
        return self.static_info.power_limit_w

    @property
    def sort_index(self) -> int | None:
        return self.static_info.sort_index

    # Legacy aliases
    @property
    def gfx(self) -> Deque[float]:
        return self.gpu_util

    @property
    def umc(self) -> Deque[float]:
        return self.mem_ctrl_util

    @property
    def hip_id(self) -> int | None:
        return self.static_info.sort_index


class GPUProvider(ABC):
    """Abstract base class for GPU metrics providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name (e.g., 'AMD', 'NVIDIA', 'Apple')."""
        pass

    @property
    @abstractmethod
    def vendor(self) -> str:
        """Vendor identifier."""
        pass

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """Check if this provider can be used on the current system."""
        pass

    @abstractmethod
    def get_gpu_count(self) -> int:
        """Return the number of GPUs available."""
        pass

    @abstractmethod
    def get_static_info(self, timeout: float = 10.0) -> Dict[int, GPUStaticInfo]:
        """Get static information for all GPUs.

        Args:
            timeout: Timeout in seconds for the operation.

        Returns:
            Dictionary mapping GPU index to static info.
        """
        pass

    @abstractmethod
    def get_metrics(self, timeout: float = 5.0) -> List[GPUMetrics]:
        """Get current metrics for all GPUs.

        Args:
            timeout: Timeout in seconds for the operation.

        Returns:
            List of metric snapshots, one per GPU.
        """
        pass

    def initialize_history(
        self, static_info: Dict[int, GPUStaticInfo], max_points: int = 600
    ) -> Dict[int, GPUHistory]:
        """Create history objects for all GPUs.

        Args:
            static_info: Static info dictionary from get_static_info().
            max_points: Maximum number of history points to retain.

        Returns:
            Dictionary mapping GPU index to history objects.
        """
        histories = {}
        for gpu_idx, info in static_info.items():
            histories[gpu_idx] = GPUHistory(static_info=info, max_points=max_points)
        return histories

    def update_history(
        self, histories: Dict[int, GPUHistory], timeout: float = 5.0
    ) -> None:
        """Update history with current metrics.

        Args:
            histories: History dictionary to update.
            timeout: Timeout for getting metrics.
        """
        metrics_list = self.get_metrics(timeout=timeout)
        for metrics in metrics_list:
            if metrics.gpu_idx in histories:
                histories[metrics.gpu_idx].add_metrics(metrics)
