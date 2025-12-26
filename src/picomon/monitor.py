"""Picomon entry point and CLI."""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Sequence

from .config import PicomonConfig
from .providers import (
    GPUProvider,
    GPUHistory,
    detect_providers,
    get_provider,
    MultiProvider,
)

__all__ = ["build_parser", "run"]

DEFAULT_CONFIG = PicomonConfig()

_LOG_LEVELS = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="picomon",
        description="Beautiful TUI dashboard for monitoring GPUs (AMD, NVIDIA, Apple Silicon)",
    )
    parser.add_argument(
        "--update-interval",
        type=float,
        default=DEFAULT_CONFIG.update_interval,
        help="Refresh interval in seconds (default: %(default)s)",
    )
    parser.add_argument(
        "--history-minutes",
        type=int,
        default=DEFAULT_CONFIG.history_minutes,
        help="How many minutes of history to retain (default: %(default)s)",
    )
    parser.add_argument(
        "--static-timeout",
        type=float,
        default=DEFAULT_CONFIG.static_timeout,
        help="Timeout (seconds) when collecting static metadata (default: %(default)s)",
    )
    parser.add_argument(
        "--metric-timeout",
        type=float,
        default=DEFAULT_CONFIG.metric_timeout,
        help="Timeout (seconds) when polling metrics (default: %(default)s)",
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=sorted(_LOG_LEVELS),
        help="Verbosity for logging diagnostics (default: %(default)s)",
    )
    parser.add_argument(
        "--provider",
        choices=["auto", "amd", "nvidia", "apple"],
        default="auto",
        help="GPU provider to use (default: auto-detect)",
    )
    parser.add_argument(
        "--classic",
        action="store_true",
        help="Use classic curses UI instead of Textual TUI",
    )
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help="List available GPU providers and exit",
    )
    return parser


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=_LOG_LEVELS.get(level.upper(), logging.WARNING),
        format="%(levelname)s: %(message)s",
    )


def _config_from_namespace(ns: argparse.Namespace) -> PicomonConfig:
    return PicomonConfig(
        update_interval=ns.update_interval,
        history_minutes=ns.history_minutes,
        static_timeout=ns.static_timeout,
        metric_timeout=ns.metric_timeout,
    )


def _get_provider(provider_name: str) -> GPUProvider | None:
    """Get the appropriate provider based on user selection."""
    if provider_name == "auto":
        # Use MultiProvider to support multiple GPU types
        providers = detect_providers()
        if not providers:
            return None
        if len(providers) == 1:
            return providers[0]
        return MultiProvider(providers)
    else:
        return get_provider(provider_name)


def run(argv: Sequence[str] | None = None) -> int:
    """Run Picomon."""
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    _configure_logging(args.log_level)
    logger = logging.getLogger("picomon")

    # Handle --list-providers
    if args.list_providers:
        providers = detect_providers()
        if providers:
            print("Available GPU providers:")
            for p in providers:
                count = p.get_gpu_count()
                print(f"  - {p.name}: {count} GPU(s)")
        else:
            print("No GPU providers detected.")
        return 0

    try:
        config = _config_from_namespace(args)
    except ValueError as exc:
        logger.error("Invalid configuration: %s", exc)
        return 2

    # Get provider
    provider = _get_provider(args.provider)
    if provider is None:
        logger.error(
            "No GPUs detected. Checked: AMD (amd-smi), NVIDIA (nvidia-smi), Apple Silicon.\n"
            "Use --list-providers to see available providers."
        )
        return 1

    # Get static info and initialize history
    static_info = provider.get_static_info(timeout=config.static_timeout)
    if not static_info:
        logger.error("Failed to get GPU information from %s provider.", provider.name)
        return 1

    logger.info("Using %s provider with %d GPU(s)", provider.name, len(static_info))

    # Initialize history
    gpus: dict[int, GPUHistory] = provider.initialize_history(
        static_info, max_points=config.max_points
    )

    # Initial metrics update
    provider.update_history(gpus, timeout=config.metric_timeout)

    def tick() -> None:
        provider.update_history(gpus, timeout=config.metric_timeout)

    if args.classic:
        # Use classic curses UI (AMD only for backwards compatibility)
        import curses
        from .ui import render_loop

        # Convert new GPUHistory to old format for classic UI
        from .history import GPUHistory as OldGPUHistory

        old_gpus: dict[int, OldGPUHistory] = {}
        for idx, hist in gpus.items():
            old_hist = OldGPUHistory(config.max_points)
            old_hist.hip_id = hist.sort_index
            old_hist.vram_total_mb = hist.vram_total_mb
            old_hist.power_limit_w = hist.power_limit_w
            old_gpus[idx] = old_hist

        def old_tick() -> None:
            tick()
            # Sync data back to old format
            for idx, hist in gpus.items():
                old_hist = old_gpus.get(idx)
                if old_hist:
                    # Copy history data
                    old_hist.timestamps.clear()
                    old_hist.timestamps.extend(hist.timestamps)
                    old_hist.gfx.clear()
                    old_hist.gfx.extend(hist.gpu_util)
                    old_hist.umc.clear()
                    old_hist.umc.extend(hist.mem_ctrl_util)
                    old_hist.power_w.clear()
                    old_hist.power_w.extend(hist.power_w)
                    old_hist.vram_used_mb.clear()
                    old_hist.vram_used_mb.extend(hist.vram_used_mb)

        try:
            curses.wrapper(render_loop, config, old_gpus, old_tick)
        except KeyboardInterrupt:
            return 0
        except curses.error as exc:
            logger.error("Curses rendering failed: %s", exc)
            return 1
    else:
        # Use new Textual TUI
        from .app import run_textual_app

        try:
            run_textual_app(config, gpus, tick)
        except KeyboardInterrupt:
            return 0
        except Exception as exc:
            logger.error("TUI failed: %s", exc)
            if args.log_level.upper() == "DEBUG":
                import traceback
                traceback.print_exc()
            return 1

    return 0
