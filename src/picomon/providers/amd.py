"""AMD GPU provider using amd-smi."""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
from datetime import datetime
from typing import Dict, List, Sequence

from .base import GPUProvider, GPUStaticInfo, GPUMetrics

__all__ = ["AMDProvider"]

logger = logging.getLogger(__name__)


def _parse_value_unit(value) -> float:
    """Parse a value that may include units or be in various formats."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        # Handle format: {"value": 123, "unit": "MB"}
        v = value.get("value")
        if v is not None:
            return float(v)
        return 0.0
    if isinstance(value, str):
        # Strip units and parse
        cleaned = value.strip().split()[0] if value.strip() else "0"
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    return 0.0


def _run_command(args: Sequence[str], timeout: float) -> str | None:
    """Run a command and return its output."""
    try:
        return subprocess.check_output(
            args,
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
        )
    except Exception as exc:
        logger.debug("Failed to run %s: %s", " ".join(args), exc)
        return None


def _run_json(args: Sequence[str], timeout: float) -> dict | list | None:
    """Run a command and parse JSON output."""
    output = _run_command(args, timeout)
    if output is None:
        return None
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        logger.debug("Failed to parse JSON: %s", exc)
        return None


def _parse_int(value) -> int | None:
    """Parse an integer value."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class AMDProvider(GPUProvider):
    """AMD GPU provider using amd-smi command-line tool."""

    @property
    def name(self) -> str:
        return "AMD"

    @property
    def vendor(self) -> str:
        return "AMD"

    @classmethod
    def is_available(cls) -> bool:
        """Check if amd-smi is available."""
        if shutil.which("amd-smi") is None:
            return False
        # Try to run it
        try:
            output = subprocess.check_output(
                ["amd-smi", "version"],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=5.0,
            )
            return "amd-smi" in output.lower() or len(output) > 0
        except Exception:
            return False

    def get_gpu_count(self) -> int:
        """Get the number of AMD GPUs."""
        data = _run_json(["amd-smi", "list", "--json"], timeout=5.0)
        if data is None:
            return 0
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            return len(data.get("gpu_data", []))
        return 0

    def _load_gpu_identity_map(self, timeout: float) -> Dict[int, int]:
        """Load GPU to HIP ID mapping."""
        data = _run_json(["amd-smi", "list", "--json"], timeout=timeout)
        if data is None:
            return {}

        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict):
            entries = data.get("gpu_data", [])
        else:
            return {}

        mapping: Dict[int, int] = {}
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            gpu_idx = _parse_int(entry.get("gpu"))
            hip_id = entry.get("hip_id")
            node_id = entry.get("node_id")
            hip_idx = _parse_int(hip_id)
            if hip_idx is None:
                hip_idx = _parse_int(node_id)
            if gpu_idx is not None and hip_idx is not None:
                mapping[gpu_idx] = hip_idx

        return mapping

    def get_static_info(self, timeout: float = 10.0) -> Dict[int, GPUStaticInfo]:
        """Get static information for all AMD GPUs."""
        data = _run_json(
            ["amd-smi", "static", "--vram", "--limit", "--json"],
            timeout=timeout,
        )
        if not data:
            return {}

        hip_ids = self._load_gpu_identity_map(timeout)
        gpus: Dict[int, GPUStaticInfo] = {}

        gpu_data = data.get("gpu_data", []) if isinstance(data, dict) else data
        for entry in gpu_data:
            gpu_id = entry.get("gpu")
            if gpu_id is None:
                continue
            try:
                gpu_idx = int(gpu_id)
            except (TypeError, ValueError):
                continue

            # Parse VRAM
            vram_block = entry.get("vram", {}) or {}
            size = vram_block.get("size")
            vram_total = _parse_value_unit(size) if size else 0.0

            # Parse power limit
            limit_block = entry.get("limit", {}) or {}
            pwr = limit_block.get("socket_power") or limit_block.get("max_power")
            power_limit = _parse_value_unit(pwr) if pwr else 0.0

            # Get GPU name from asic block
            asic_block = entry.get("asic", {}) or {}
            gpu_name = asic_block.get("market_name") or asic_block.get("name") or "AMD GPU"

            info = GPUStaticInfo(
                gpu_idx=gpu_idx,
                name=gpu_name,
                vendor="AMD",
                vram_total_mb=vram_total,
                power_limit_w=power_limit,
                sort_index=hip_ids.get(gpu_idx),
            )
            gpus[gpu_idx] = info

        return gpus

    def get_metrics(self, timeout: float = 5.0) -> List[GPUMetrics]:
        """Get current metrics for all AMD GPUs."""
        data = _run_json(
            ["amd-smi", "metric", "--usage", "--power", "--mem-usage", "--json"],
            timeout=timeout,
        )
        if not data:
            return []

        ts = datetime.now()
        metrics_list: List[GPUMetrics] = []

        gpu_data = data.get("gpu_data", []) if isinstance(data, dict) else data
        for entry in gpu_data:
            gpu_id = entry.get("gpu")
            if gpu_id is None:
                continue
            try:
                gpu_idx = int(gpu_id)
            except (TypeError, ValueError):
                continue

            # Usage metrics
            usage = entry.get("usage", {}) or {}
            gfx = max(0.0, min(100.0, _parse_value_unit(usage.get("gfx_activity", 0))))
            umc = max(0.0, min(100.0, _parse_value_unit(usage.get("umc_activity", 0))))

            # Power
            power_block = entry.get("power", {}) or {}
            socket_pwr = power_block.get("socket_power") or power_block.get("SOCKET_POWER")
            power_w = _parse_value_unit(socket_pwr) if socket_pwr else 0.0

            # Memory usage
            mem_usage = entry.get("mem_usage", {}) or {}
            used = mem_usage.get("used_visible_vram") or mem_usage.get("used_vram")
            vram_used = _parse_value_unit(used) if used else 0.0

            # Temperature (if available)
            temp_block = entry.get("temperature", {}) or {}
            temp = temp_block.get("edge") or temp_block.get("hotspot")
            temperature = _parse_value_unit(temp) if temp else None

            metrics = GPUMetrics(
                timestamp=ts,
                gpu_idx=gpu_idx,
                gpu_utilization=gfx,
                memory_controller_utilization=umc,
                power_draw_w=power_w,
                vram_used_mb=vram_used,
                temperature_c=temperature,
            )
            metrics_list.append(metrics)

        return metrics_list
