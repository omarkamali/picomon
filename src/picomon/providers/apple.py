"""Apple Silicon GPU provider for macOS."""

from __future__ import annotations

import logging
import platform
import plistlib
import subprocess
import re
from datetime import datetime
from typing import Dict, List, Any

from .base import GPUProvider, GPUStaticInfo, GPUMetrics

__all__ = ["AppleSiliconProvider"]

logger = logging.getLogger(__name__)


def _run_command(args: List[str], timeout: float = 5.0) -> str | None:
    """Run a command and return its output."""
    try:
        return subprocess.check_output(
            args,
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
        )
    except Exception as exc:
        logger.debug("Command failed: %s - %s", " ".join(args), exc)
        return None


def _get_soc_info() -> Dict[str, Any]:
    """Get Apple Silicon SoC information using system_profiler."""
    try:
        output = subprocess.check_output(
            ["system_profiler", "SPHardwareDataType", "-xml"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=10.0,
        )
        plist = plistlib.loads(output.encode())
        if plist and len(plist) > 0:
            items = plist[0].get("_items", [])
            if items:
                return items[0]
    except Exception as exc:
        logger.debug("Failed to get SoC info: %s", exc)
    return {}


def _get_gpu_cores() -> int:
    """Get the number of GPU cores."""
    try:
        output = subprocess.check_output(
            ["sysctl", "-n", "hw.perflevel0.logicalcpu"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=5.0,
        )
        # This doesn't give GPU cores directly, but we can estimate from chip name
    except Exception:
        pass

    # Try to get from system_profiler
    try:
        output = subprocess.check_output(
            ["system_profiler", "SPDisplaysDataType"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=10.0,
        )
        # Look for "Total Number of Cores" line
        match = re.search(r"Total Number of Cores:\s*(\d+)", output)
        if match:
            return int(match.group(1))
    except Exception:
        pass

    return 0


def _get_memory_info() -> Dict[str, float]:
    """Get memory information including unified memory used by GPU."""
    info = {"total_mb": 0.0, "used_mb": 0.0, "available_mb": 0.0}

    try:
        output = subprocess.check_output(
            ["sysctl", "-n", "hw.memsize"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=5.0,
        )
        info["total_mb"] = int(output.strip()) / (1024 * 1024)
    except Exception:
        pass

    # Use vm_stat for memory usage
    try:
        output = subprocess.check_output(
            ["vm_stat"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=5.0,
        )
        # Parse vm_stat output
        pages_active = 0
        pages_wired = 0
        pages_compressed = 0
        page_size = 16384  # Default for Apple Silicon

        for line in output.split("\n"):
            if "page size of" in line:
                match = re.search(r"page size of (\d+) bytes", line)
                if match:
                    page_size = int(match.group(1))
            elif "Pages active:" in line:
                match = re.search(r"Pages active:\s*(\d+)", line)
                if match:
                    pages_active = int(match.group(1))
            elif "Pages wired down:" in line:
                match = re.search(r"Pages wired down:\s*(\d+)", line)
                if match:
                    pages_wired = int(match.group(1))
            elif "Pages occupied by compressor:" in line:
                match = re.search(r"Pages occupied by compressor:\s*(\d+)", line)
                if match:
                    pages_compressed = int(match.group(1))

        used_bytes = (pages_active + pages_wired + pages_compressed) * page_size
        info["used_mb"] = used_bytes / (1024 * 1024)
        info["available_mb"] = info["total_mb"] - info["used_mb"]
    except Exception:
        pass

    return info


def _get_gpu_utilization() -> float:
    """Get GPU utilization from powermetrics (requires sudo for accurate data)."""
    # Try to read from powermetrics if available
    # Note: powermetrics requires sudo, so we'll use a fallback approach

    # Fallback: Use ioreg to check GPU activity
    try:
        output = subprocess.check_output(
            ["ioreg", "-r", "-c", "IOAccelerator", "-d", "1"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=5.0,
        )
        # Look for performance state or utilization hints
        # This is approximate since Apple doesn't expose direct GPU utilization
        if "PerformanceStatistics" in output:
            # GPU is active
            return 50.0  # Estimate - GPU is being used
    except Exception:
        pass

    return 0.0


def _get_power_metrics() -> Dict[str, float]:
    """Get power metrics (limited on macOS without sudo)."""
    metrics = {"cpu_power_w": 0.0, "gpu_power_w": 0.0, "total_power_w": 0.0}

    # Power metrics require sudo on macOS
    # We'll provide estimates based on activity

    # Use top to estimate activity level
    try:
        output = subprocess.check_output(
            ["ps", "-A", "-o", "%cpu"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=5.0,
        )
        total_cpu = 0.0
        for line in output.strip().split("\n")[1:]:
            try:
                total_cpu += float(line.strip())
            except ValueError:
                pass
        # Rough estimate: M1/M2/M3 chips use ~5-15W under load
        # Scale based on CPU activity
        cpu_ratio = min(1.0, total_cpu / 800.0)  # 800% = full 8-core utilization
        metrics["cpu_power_w"] = 2.0 + (cpu_ratio * 12.0)  # 2-14W range
        metrics["gpu_power_w"] = 1.0 + (cpu_ratio * 5.0)  # 1-6W estimate for GPU
        metrics["total_power_w"] = metrics["cpu_power_w"] + metrics["gpu_power_w"]
    except Exception:
        pass

    return metrics


class AppleSiliconProvider(GPUProvider):
    """Apple Silicon GPU provider for macOS.

    Note: Apple Silicon uses unified memory, so GPU "VRAM" is shared with system RAM.
    Power metrics are estimates since accurate readings require sudo.
    """

    @property
    def name(self) -> str:
        return "Apple Silicon"

    @property
    def vendor(self) -> str:
        return "Apple"

    @classmethod
    def is_available(cls) -> bool:
        """Check if running on Apple Silicon macOS."""
        if platform.system() != "Darwin":
            return False

        # Check if it's Apple Silicon
        try:
            output = subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=5.0,
            )
            return "Apple" in output
        except Exception:
            pass

        # Alternative check
        try:
            output = subprocess.check_output(
                ["uname", "-m"],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=5.0,
            )
            return "arm64" in output
        except Exception:
            return False

    def _get_chip_name(self) -> str:
        """Get the Apple Silicon chip name."""
        soc_info = _get_soc_info()
        chip_name = soc_info.get("chip_type", "")
        if chip_name:
            return chip_name

        # Fallback: try sysctl
        try:
            output = subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=5.0,
            )
            return output.strip()
        except Exception:
            pass

        return "Apple Silicon"

    def get_gpu_count(self) -> int:
        """Apple Silicon has integrated GPU - return 1."""
        if self.is_available():
            return 1
        return 0

    def get_static_info(self, timeout: float = 10.0) -> Dict[int, GPUStaticInfo]:
        """Get static information for Apple Silicon GPU."""
        if not self.is_available():
            return {}

        chip_name = self._get_chip_name()
        gpu_cores = _get_gpu_cores()
        memory_info = _get_memory_info()

        # Apple Silicon uses unified memory
        # GPU can potentially use most of system RAM
        # Report total system memory as available for GPU
        vram_total = memory_info.get("total_mb", 0.0)

        # Estimate power limits based on chip
        power_limit = 30.0  # Default estimate
        if "M1" in chip_name:
            power_limit = 25.0 if "Pro" in chip_name else 20.0
            if "Max" in chip_name:
                power_limit = 40.0
            if "Ultra" in chip_name:
                power_limit = 60.0
        elif "M2" in chip_name:
            power_limit = 25.0 if "Pro" in chip_name else 22.0
            if "Max" in chip_name:
                power_limit = 45.0
            if "Ultra" in chip_name:
                power_limit = 65.0
        elif "M3" in chip_name:
            power_limit = 28.0 if "Pro" in chip_name else 24.0
            if "Max" in chip_name:
                power_limit = 50.0
        elif "M4" in chip_name:
            power_limit = 30.0 if "Pro" in chip_name else 26.0
            if "Max" in chip_name:
                power_limit = 55.0

        info = GPUStaticInfo(
            gpu_idx=0,
            name=f"{chip_name} GPU",
            vendor="Apple",
            architecture="Apple GPU",
            compute_units=gpu_cores,
            vram_total_mb=vram_total,  # Unified memory
            power_limit_w=power_limit,
            sort_index=0,
        )

        return {0: info}

    def get_metrics(self, timeout: float = 5.0) -> List[GPUMetrics]:
        """Get current metrics for Apple Silicon GPU."""
        if not self.is_available():
            return []

        ts = datetime.now()
        memory_info = _get_memory_info()
        power_info = _get_power_metrics()
        gpu_util = _get_gpu_utilization()

        # Use system memory usage as VRAM usage (unified memory)
        vram_used = memory_info.get("used_mb", 0.0)

        # Memory controller utilization approximation
        mem_util = 0.0
        if memory_info.get("total_mb", 0) > 0:
            mem_util = (vram_used / memory_info["total_mb"]) * 100

        metrics = GPUMetrics(
            timestamp=ts,
            gpu_idx=0,
            gpu_utilization=gpu_util,
            memory_controller_utilization=mem_util,
            power_draw_w=power_info.get("gpu_power_w", 0.0),
            vram_used_mb=vram_used,
            temperature_c=None,  # Not easily available without sudo
        )

        return [metrics]
