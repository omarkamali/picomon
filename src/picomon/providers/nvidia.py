"""NVIDIA GPU provider using nvidia-smi."""

from __future__ import annotations

import logging
import shutil
import subprocess
from datetime import datetime
from typing import Dict, List

from .base import GPUProvider, GPUStaticInfo, GPUMetrics

__all__ = ["NVIDIAProvider"]

logger = logging.getLogger(__name__)


def _run_nvidia_smi(query_fields: List[str], timeout: float = 5.0) -> List[Dict[str, str]] | None:
    """Run nvidia-smi with query and return parsed results.

    Args:
        query_fields: List of fields to query (e.g., ['name', 'memory.total']).
        timeout: Command timeout.

    Returns:
        List of dictionaries with field values for each GPU, or None on error.
    """
    query = ",".join(query_fields)
    try:
        output = subprocess.check_output(
            [
                "nvidia-smi",
                f"--query-gpu={query}",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
        )
    except Exception as exc:
        logger.debug("nvidia-smi failed: %s", exc)
        return None

    results = []
    for line in output.strip().split("\n"):
        if not line.strip():
            continue
        values = [v.strip() for v in line.split(",")]
        if len(values) == len(query_fields):
            results.append(dict(zip(query_fields, values)))

    return results


def _parse_float(value: str) -> float:
    """Parse a float value, returning 0.0 on error."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _parse_int(value: str) -> int | None:
    """Parse an integer value."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class NVIDIAProvider(GPUProvider):
    """NVIDIA GPU provider using nvidia-smi command-line tool."""

    @property
    def name(self) -> str:
        return "NVIDIA"

    @property
    def vendor(self) -> str:
        return "NVIDIA"

    @classmethod
    def is_available(cls) -> bool:
        """Check if nvidia-smi is available."""
        if shutil.which("nvidia-smi") is None:
            return False
        try:
            output = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=5.0,
            )
            return len(output.strip()) > 0
        except Exception:
            return False

    def get_gpu_count(self) -> int:
        """Get the number of NVIDIA GPUs."""
        try:
            output = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=5.0,
            )
            return len([l for l in output.strip().split("\n") if l.strip()])
        except Exception:
            return 0

    def get_static_info(self, timeout: float = 10.0) -> Dict[int, GPUStaticInfo]:
        """Get static information for all NVIDIA GPUs."""
        fields = [
            "index",
            "name",
            "memory.total",
            "power.limit",
            "pci.bus_id",
        ]
        results = _run_nvidia_smi(fields, timeout=timeout)
        if not results:
            return {}

        gpus: Dict[int, GPUStaticInfo] = {}
        for entry in results:
            idx = _parse_int(entry.get("index", ""))
            if idx is None:
                continue

            # Memory is reported in MiB
            vram_total = _parse_float(entry.get("memory.total", "0"))

            # Power limit is in watts
            power_limit = _parse_float(entry.get("power.limit", "0"))

            info = GPUStaticInfo(
                gpu_idx=idx,
                name=entry.get("name", "NVIDIA GPU"),
                vendor="NVIDIA",
                vram_total_mb=vram_total,
                power_limit_w=power_limit,
                pcie_bus=entry.get("pci.bus_id", ""),
                sort_index=idx,
            )
            gpus[idx] = info

        return gpus

    def get_metrics(self, timeout: float = 5.0) -> List[GPUMetrics]:
        """Get current metrics for all NVIDIA GPUs."""
        fields = [
            "index",
            "utilization.gpu",
            "utilization.memory",
            "power.draw",
            "memory.used",
            "temperature.gpu",
            "clocks.current.graphics",
            "clocks.current.memory",
            "fan.speed",
        ]
        results = _run_nvidia_smi(fields, timeout=timeout)
        if not results:
            return []

        ts = datetime.now()
        metrics_list: List[GPUMetrics] = []

        for entry in results:
            idx = _parse_int(entry.get("index", ""))
            if idx is None:
                continue

            # Parse metrics
            gpu_util = _parse_float(entry.get("utilization.gpu", "0"))
            mem_util = _parse_float(entry.get("utilization.memory", "0"))
            power_draw = _parse_float(entry.get("power.draw", "0"))
            vram_used = _parse_float(entry.get("memory.used", "0"))

            # Optional metrics
            temp_str = entry.get("temperature.gpu", "")
            temperature = _parse_float(temp_str) if temp_str and temp_str != "[N/A]" else None

            gpu_clock_str = entry.get("clocks.current.graphics", "")
            gpu_clock = _parse_int(gpu_clock_str) if gpu_clock_str and gpu_clock_str != "[N/A]" else None

            mem_clock_str = entry.get("clocks.current.memory", "")
            mem_clock = _parse_int(mem_clock_str) if mem_clock_str and mem_clock_str != "[N/A]" else None

            fan_str = entry.get("fan.speed", "")
            fan_speed = _parse_float(fan_str) if fan_str and fan_str != "[N/A]" else None

            metrics = GPUMetrics(
                timestamp=ts,
                gpu_idx=idx,
                gpu_utilization=gpu_util,
                memory_controller_utilization=mem_util,
                power_draw_w=power_draw,
                vram_used_mb=vram_used,
                temperature_c=temperature,
                gpu_clock_mhz=gpu_clock,
                memory_clock_mhz=mem_clock,
                fan_speed_percent=fan_speed,
            )
            metrics_list.append(metrics)

        return metrics_list
