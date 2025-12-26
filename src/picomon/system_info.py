"""System information collection (CPU, RAM, etc.)."""

from __future__ import annotations

import platform
import socket
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
from typing import Deque

import psutil


@dataclass
class SystemInfo:
    """Static system information."""

    hostname: str = ""
    os_name: str = ""
    os_version: str = ""
    kernel: str = ""
    cpu_model: str = ""
    cpu_cores_physical: int = 0
    cpu_cores_logical: int = 0
    ram_total_gb: float = 0.0
    swap_total_gb: float = 0.0
    boot_time: datetime | None = None

    @property
    def uptime(self) -> timedelta:
        """Get system uptime."""
        if self.boot_time is None:
            return timedelta()
        return datetime.now() - self.boot_time

    @property
    def uptime_str(self) -> str:
        """Get formatted uptime string."""
        uptime = self.uptime
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        else:
            return f"{minutes}m {seconds}s"


@dataclass
class SystemMetrics:
    """Dynamic system metrics with history."""

    max_points: int = 600

    # Current values
    cpu_percent: float = 0.0
    ram_used_gb: float = 0.0
    ram_total_gb: float = 0.0
    swap_used_gb: float = 0.0
    swap_total_gb: float = 0.0
    load_1m: float = 0.0
    load_5m: float = 0.0
    load_15m: float = 0.0

    # History
    timestamps: Deque[datetime] = field(default_factory=deque)
    cpu_history: Deque[float] = field(default_factory=deque)
    ram_history: Deque[float] = field(default_factory=deque)

    def __post_init__(self):
        """Initialize deques with max length."""
        self.timestamps = deque(maxlen=self.max_points)
        self.cpu_history = deque(maxlen=self.max_points)
        self.ram_history = deque(maxlen=self.max_points)

    def add_sample(self, timestamp: datetime, cpu: float, ram_used: float):
        """Add a new sample to history."""
        self.timestamps.append(timestamp)
        self.cpu_history.append(cpu)
        self.ram_history.append(ram_used)
        self.cpu_percent = cpu
        self.ram_used_gb = ram_used

    @property
    def ram_percent(self) -> float:
        """RAM usage percentage."""
        if self.ram_total_gb <= 0:
            return 0.0
        return (self.ram_used_gb / self.ram_total_gb) * 100

    @property
    def swap_percent(self) -> float:
        """Swap usage percentage."""
        if self.swap_total_gb <= 0:
            return 0.0
        return (self.swap_used_gb / self.swap_total_gb) * 100


def get_cpu_model() -> str:
    """Get CPU model name."""
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":")[1].strip()
    except (FileNotFoundError, IOError):
        pass
    return platform.processor() or "Unknown"


def load_system_info() -> SystemInfo:
    """Load static system information."""
    info = SystemInfo()

    # Basic info
    info.hostname = socket.gethostname()
    info.os_name = platform.system()
    info.os_version = platform.release()
    info.kernel = platform.release()

    # Try to get better OS info on Linux
    try:
        import distro
        info.os_name = f"{distro.name()} {distro.version()}"
    except ImportError:
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        info.os_name = line.split("=")[1].strip().strip('"')
                        break
        except (FileNotFoundError, IOError):
            info.os_name = f"{platform.system()} {platform.release()}"

    # CPU info
    info.cpu_model = get_cpu_model()
    info.cpu_cores_physical = psutil.cpu_count(logical=False) or 0
    info.cpu_cores_logical = psutil.cpu_count(logical=True) or 0

    # Memory
    mem = psutil.virtual_memory()
    info.ram_total_gb = mem.total / (1024**3)

    swap = psutil.swap_memory()
    info.swap_total_gb = swap.total / (1024**3)

    # Boot time
    info.boot_time = datetime.fromtimestamp(psutil.boot_time())

    return info


def update_system_metrics(metrics: SystemMetrics) -> None:
    """Update dynamic system metrics."""
    now = datetime.now()

    # CPU
    cpu_percent = psutil.cpu_percent(interval=None)

    # Memory
    mem = psutil.virtual_memory()
    metrics.ram_total_gb = mem.total / (1024**3)
    ram_used = mem.used / (1024**3)

    swap = psutil.swap_memory()
    metrics.swap_total_gb = swap.total / (1024**3)
    metrics.swap_used_gb = swap.used / (1024**3)

    # Load average (Unix only)
    try:
        load = psutil.getloadavg()
        metrics.load_1m = load[0]
        metrics.load_5m = load[1]
        metrics.load_15m = load[2]
    except (AttributeError, OSError):
        metrics.load_1m = 0.0
        metrics.load_5m = 0.0
        metrics.load_15m = 0.0

    # Add to history
    metrics.add_sample(now, cpu_percent, ram_used)
