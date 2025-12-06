from __future__ import annotations

import argparse
import logging
from typing import Sequence

import curses

from .config import PicomonConfig
from .smi import load_static_info, update_dynamic_info
from .ui import render_loop

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
        description="Minimal AMD GPU dashboard with curses UI",
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
        default="INFO",
        choices=sorted(_LOG_LEVELS),
        help="Verbosity for logging diagnostics (default: %(default)s)",
    )
    return parser


def _configure_logging(level: str) -> None:
    logging.basicConfig(level=_LOG_LEVELS.get(level.upper(), logging.INFO))


def _config_from_namespace(ns: argparse.Namespace) -> PicomonConfig:
    return PicomonConfig(
        update_interval=ns.update_interval,
        history_minutes=ns.history_minutes,
        static_timeout=ns.static_timeout,
        metric_timeout=ns.metric_timeout,
    )


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    _configure_logging(args.log_level)
    logger = logging.getLogger("picomon")

    try:
        config = _config_from_namespace(args)
    except ValueError as exc:
        logger.error("Invalid configuration: %s", exc)
        return 2

    gpus = load_static_info(config)
    if not gpus:
        logger.error(
            "No GPUs detected via amd-smi static metrics. Check permissions/install."
        )
        return 1

    update_dynamic_info(config, gpus)

    def tick() -> None:
        update_dynamic_info(config, gpus)

    try:
        curses.wrapper(render_loop, config, gpus, tick)
    except KeyboardInterrupt:  # pragma: no cover - user initiated
        return 0
    except curses.error as exc:
        logger.error("Curses rendering failed: %s", exc)
        return 1

    return 0
