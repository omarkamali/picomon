from __future__ import annotations

import json
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Protocol, Sequence

from .config import PicomonConfig
from .history import GPUHistory, parse_value_unit

__all__ = ["load_static_info", "update_dynamic_info"]

logger = logging.getLogger(__name__)


class CommandRunner(Protocol):
    def __call__(self, args: Sequence[str], *, timeout: float) -> str: ...


def _default_runner(args: Sequence[str], *, timeout: float) -> str:
    return subprocess.check_output(  # type: ignore[return-value]
        args,
        text=True,
        stderr=subprocess.DEVNULL,
        timeout=timeout,
    )


def _run_json(
    args: Sequence[str], *, timeout: float, runner: CommandRunner
) -> dict | list | None:
    try:
        output = runner(args, timeout=timeout)
    except Exception as exc:  # pragma: no cover - just log
        logger.debug("Failed to run %s: %s", " ".join(args), exc)
        return None

    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:  # pragma: no cover - unexpected
        logger.debug("Failed to parse amd-smi json: %s", exc)
        return None


def _parse_int(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _load_gpu_identity_map(
    config: PicomonConfig, runner: CommandRunner
) -> Dict[int, int]:
    data = _run_json(
        ["amd-smi", "list", "--json"],
        timeout=config.static_timeout,
        runner=runner,
    )
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
        if gpu_idx is None or hip_idx is None:
            continue
        mapping[gpu_idx] = hip_idx

    return mapping


def load_static_info(
    config: PicomonConfig, *, runner: CommandRunner | None = None
) -> Dict[int, GPUHistory]:
    """Return GPU histories seeded with static data from amd-smi."""

    runner = runner or _default_runner
    data = _run_json(
        ["amd-smi", "static", "--vram", "--limit", "--json"],
        timeout=config.static_timeout,
        runner=runner,
    )
    if not data:
        return {}

    hip_ids = _load_gpu_identity_map(config, runner)
    gpus: Dict[int, GPUHistory] = {}
    for entry in data.get("gpu_data", []):
        gpu_id = entry.get("gpu")
        if gpu_id is None:
            continue
        try:
            gpu_idx = int(gpu_id)
        except (TypeError, ValueError):
            continue

        hist = GPUHistory(config.max_points)
        hist.hip_id = hip_ids.get(gpu_idx)

        vram_block = entry.get("vram", {}) or {}
        size = vram_block.get("size")
        if size is not None:
            hist.vram_total_mb = parse_value_unit(size)

        limit_block = entry.get("limit", {}) or {}
        pwr = limit_block.get("socket_power") or limit_block.get("max_power")
        if pwr is not None:
            hist.power_limit_w = parse_value_unit(pwr)

        gpus[gpu_idx] = hist

    return gpus


def update_dynamic_info(
    config: PicomonConfig,
    gpus: Dict[int, GPUHistory],
    *,
    runner: CommandRunner | None = None,
    timestamp_provider=datetime.now,
) -> None:
    """Add a fresh sample for each GPU in-place."""

    runner = runner or _default_runner
    data = _run_json(
        [
            "amd-smi",
            "metric",
            "--usage",
            "--power",
            "--mem-usage",
            "--json",
        ],
        timeout=config.metric_timeout,
        runner=runner,
    )
    if not data:
        return

    ts = timestamp_provider()
    for entry in data.get("gpu_data", []):
        gpu_id = entry.get("gpu")
        if gpu_id is None:
            continue
        try:
            gpu_idx = int(gpu_id)
        except (TypeError, ValueError):
            continue

        hist = gpus.get(gpu_idx)
        if hist is None:
            hist = gpus[gpu_idx] = GPUHistory(config.max_points)

        usage = entry.get("usage", {}) or {}
        gfx = max(0.0, min(100.0, parse_value_unit(usage.get("gfx_activity", 0))))
        umc = max(0.0, min(100.0, parse_value_unit(usage.get("umc_activity", 0))))

        power_block = entry.get("power", {}) or {}
        socket_pwr = power_block.get("socket_power") or power_block.get("SOCKET_POWER")
        power_w = parse_value_unit(socket_pwr) if socket_pwr is not None else 0.0

        mem_usage = entry.get("mem_usage", {}) or {}
        used = mem_usage.get("used_visible_vram") or mem_usage.get("used_vram")
        total = mem_usage.get("total_visible_vram") or mem_usage.get("total_vram")
        vram_used_mb = parse_value_unit(used) if used is not None else 0.0
        if total is not None:
            total_mb = parse_value_unit(total)
            if total_mb > 0:
                hist.vram_total_mb = total_mb

        hist.add_sample(ts, gfx, umc, power_w, vram_used_mb)

    cutoff = ts - timedelta(minutes=config.history_minutes)
    for hist in gpus.values():
        hist.prune_before(cutoff)
