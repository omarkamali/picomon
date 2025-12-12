from __future__ import annotations

import curses
import time
from typing import Callable, Dict

from .config import PicomonConfig
from .history import GPUHistory

__all__ = ["sparkline", "draw_gpu_box", "render_loop"]

SPARK_BARS = "▁▂▃▄▅▆▇█"


def sparkline(values, width: int, vmax: float | None) -> tuple[str, str]:
    """Return a two-row sparkline string for the provided samples."""

    if width <= 0:
        return "".ljust(0), "".ljust(0)
    vals = list(values)
    n = len(vals)
    if n == 0:
        return " " * width, " " * width

    if vmax is None or vmax <= 0:
        vmax = max(vals) if max(vals) > 0 else 1.0

    nb = len(SPARK_BARS)
    top_row: list[str] = []
    bot_row: list[str] = []

    for col in range(width):
        if width == 1:
            idx = n - 1
        else:
            idx = int(col * (n - 1) / (width - 1))
        v = vals[idx]
        frac = max(0.0, min(1.0, v / vmax))

        if frac <= 0.5:
            bot_frac = frac * 2.0
            level = int(round(bot_frac * (nb - 1)))
            bot_ch = SPARK_BARS[level]
            top_ch = " "
        else:
            bot_ch = SPARK_BARS[-1]
            top_frac = (frac - 0.5) * 2.0
            level = int(round(top_frac * (nb - 1)))
            top_ch = SPARK_BARS[level]

        top_row.append(top_ch)
        bot_row.append(bot_ch)

    return "".join(top_row), "".join(bot_row)


def draw_gpu_box(win, gpu_id: int, hist: GPUHistory) -> None:
    win.box()
    box_h, box_w = win.getmaxyx()
    inner_w = box_w - 2
    spark_w = max(16, inner_w - 6)

    if hist.timestamps:
        gfx_now = hist.gfx[-1]
        umc_now = hist.umc[-1]
        pwr_now = hist.power_w[-1]
        vram_now = hist.vram_used_mb[-1]
    else:
        gfx_now = umc_now = pwr_now = vram_now = 0.0

    pwr_lim = hist.power_limit_w if hist.power_limit_w > 0 else 1.0
    vram_tot = hist.vram_total_mb if hist.vram_total_mb > 0 else 1.0

    pwr_pct = 100.0 * pwr_now / pwr_lim
    vram_pct = 100.0 * vram_now / vram_tot

    header = (
        f"GPU {gpu_id}  "
        f"GFX {gfx_now:3.0f}%  "
        f"UMC {umc_now:3.0f}%  "
        f"PWR {pwr_now:4.0f}/{pwr_lim:4.0f}W ({pwr_pct:3.0f}%)  "
        f"VRAM {vram_now/1024:4.1f}/{vram_tot/1024:4.1f}GB ({vram_pct:3.0f}%)"
    )
    win.addnstr(1, 1, header, inner_w)

    top, bot = sparkline(hist.gfx, spark_w, 100.0)
    win.addnstr(2, 1, "GFX ", inner_w)
    win.addnstr(2, 5, top, spark_w)
    win.addnstr(3, 5, bot, spark_w)

    top, bot = sparkline(hist.power_w, spark_w, hist.power_limit_w or None)
    win.addnstr(4, 1, "PWR ", inner_w)
    win.addnstr(4, 5, top, spark_w)
    win.addnstr(5, 5, bot, spark_w)

    top, bot = sparkline(hist.vram_used_mb, spark_w, hist.vram_total_mb or None)
    win.addnstr(6, 1, "VRM ", inner_w)
    win.addnstr(6, 5, top, spark_w)
    win.addnstr(7, 5, bot, spark_w)


def render_loop(
    stdscr,
    config: PicomonConfig,
    gpus: Dict[int, GPUHistory],
    tick: Callable[[], None],
) -> None:
    curses.curs_set(0)
    stdscr.nodelay(True)

    while True:
        tick()

        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()

        title = f"picomon (last {config.history_minutes} min) - q to quit"
        stdscr.addnstr(0, 0, title, max_x - 1)
        stdscr.hline(1, 0, curses.ACS_HLINE, max_x - 1)

        box_h = 9
        total_cols = 2
        col_w = (max_x - 3) // total_cols
        col_x = [1, 1 + col_w + 1]

        sorted_gpus = sorted(
            gpus.items(),
            key=lambda item: (
                item[1].hip_id if item[1].hip_id is not None else item[0],
                item[0],
            ),
        )
        for idx, (gpu_id, hist) in enumerate(sorted_gpus):
            col = 0 if idx < 4 else 1
            row_idx = idx if idx < 4 else idx - 4
            top = 2 + row_idx * box_h
            if top + box_h >= max_y:
                continue

            x = col_x[col]
            win = stdscr.derwin(box_h, col_w, top, x)
            draw_gpu_box(win, gpu_id, hist)

        stdscr.refresh()

        end_time = time.time() + config.update_interval
        while time.time() < end_time:
            ch = stdscr.getch()
            if ch in (ord("q"), ord("Q")):
                return
            time.sleep(0.1)
