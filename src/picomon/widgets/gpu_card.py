"""GPU card widget for the dashboard."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text
from rich.style import Style

if TYPE_CHECKING:
    from ..history import GPUHistory


# Unicode block characters
BLOCKS = " ▁▂▃▄▅▆▇█"


def render_bar(ratio: float, width: int = 20) -> tuple[str, str]:
    """Render a progress bar.

    Returns:
        Tuple of (bar_string, color).
    """
    ratio = max(0.0, min(1.0, ratio))
    filled = int(width * ratio)
    empty = width - filled

    if ratio >= 0.9:
        color = "#e74c3c"  # Red
    elif ratio >= 0.7:
        color = "#f39c12"  # Orange
    else:
        color = "#16c79a"  # Green

    bar = "\u2588" * filled + "\u2591" * empty
    return bar, color


def render_mini_sparkline(data: list[float], max_val: float, width: int = 30) -> str:
    """Render a single-row sparkline."""
    if not data:
        return " " * width

    # Sample data to fit width
    if len(data) > width:
        step = len(data) / width
        data = [data[int(i * step)] for i in range(width)]
    elif len(data) < width:
        padding = width - len(data)
        data = [0.0] * padding + data

    # Normalize and render
    if max_val <= 0:
        max_val = 1.0

    result = []
    nb = len(BLOCKS) - 1

    for val in data:
        normalized = max(0.0, min(1.0, val / max_val))
        level = int(normalized * nb)
        result.append(BLOCKS[level])

    return "".join(result)


class GPUCard(Widget):
    """A card widget displaying GPU metrics."""

    DEFAULT_CSS = """
    GPUCard {
        height: auto;
        min-height: 11;
        padding: 1;
        background: #16213e;
        border: solid #0f3460;
        margin: 0 0 1 0;
    }

    GPUCard:hover {
        border: solid #e94560;
    }

    GPUCard:focus {
        border: solid #16c79a;
    }
    """

    can_focus = True

    class Selected(Message):
        """Message sent when GPU card is selected."""

        def __init__(self, gpu_idx: int) -> None:
            self.gpu_idx = gpu_idx
            super().__init__()

    def __init__(
        self,
        gpu_idx: int,
        gpu_name: str = "GPU",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.gpu_idx = gpu_idx
        self.gpu_name = gpu_name
        self._gfx = 0.0
        self._umc = 0.0
        self._power = 0.0
        self._power_limit = 100.0
        self._vram_used = 0.0
        self._vram_total = 1.0
        self._gfx_history: list[float] = []
        self._power_history: list[float] = []

    def update_metrics(
        self,
        gfx: float,
        umc: float,
        power: float,
        power_limit: float,
        vram_used: float,
        vram_total: float,
        gfx_history: list[float],
        power_history: list[float],
    ) -> None:
        """Update the GPU metrics."""
        self._gfx = gfx
        self._umc = umc
        self._power = power
        self._power_limit = power_limit or 1.0
        self._vram_used = vram_used
        self._vram_total = vram_total or 1.0
        self._gfx_history = list(gfx_history)
        self._power_history = list(power_history)
        self.refresh()

    def on_click(self) -> None:
        """Handle click events."""
        self.post_message(self.Selected(self.gpu_idx))

    def on_key(self, event) -> None:
        """Handle key events."""
        if event.key == "enter":
            self.post_message(self.Selected(self.gpu_idx))
            event.stop()

    def render(self) -> Text:
        """Render the GPU card."""
        text = Text()
        width = max(30, self.size.width - 4)
        bar_width = max(10, width - 20)
        spark_width = max(15, width - 10)

        # Title
        text.append(f"GPU {self.gpu_idx}", style=Style(color="#e94560", bold=True))
        text.append(f"  {self.gpu_name}\n", style=Style(color="#888888"))
        text.append("\n")

        # GFX bar
        gfx_ratio = self._gfx / 100.0
        gfx_bar, gfx_color = render_bar(gfx_ratio, bar_width)
        text.append("GFX   ", style=Style(color="#888888"))
        text.append(gfx_bar, style=Style(color=gfx_color))
        text.append(f" {self._gfx:5.1f}%\n", style=Style(color="#eaeaea"))

        # UMC bar
        umc_ratio = self._umc / 100.0
        umc_bar, umc_color = render_bar(umc_ratio, bar_width)
        text.append("UMC   ", style=Style(color="#888888"))
        text.append(umc_bar, style=Style(color=umc_color))
        text.append(f" {self._umc:5.1f}%\n", style=Style(color="#eaeaea"))

        # Power bar
        pwr_ratio = self._power / self._power_limit
        pwr_bar, pwr_color = render_bar(pwr_ratio, bar_width)
        text.append("PWR   ", style=Style(color="#888888"))
        text.append(pwr_bar, style=Style(color=pwr_color))
        text.append(f" {self._power:5.0f}W\n", style=Style(color="#eaeaea"))
        text.append(f"      {'':>{bar_width}s} /{self._power_limit:.0f}W\n", style=Style(color="#666666"))

        # VRAM bar
        vram_ratio = self._vram_used / self._vram_total
        vram_bar, vram_color = render_bar(vram_ratio, bar_width)
        vram_used_gb = self._vram_used / 1024
        vram_total_gb = self._vram_total / 1024
        text.append("VRAM  ", style=Style(color="#888888"))
        text.append(vram_bar, style=Style(color=vram_color))
        text.append(f" {vram_ratio * 100:5.1f}%\n", style=Style(color="#eaeaea"))
        text.append(
            f"      {vram_used_gb:.1f} / {vram_total_gb:.1f} GB\n",
            style=Style(color="#666666"),
        )

        # Sparklines
        text.append("\n")
        gfx_spark = render_mini_sparkline(self._gfx_history, 100.0, spark_width)
        text.append(gfx_spark, style=Style(color="#16c79a"))
        text.append(" GFX\n", style=Style(color="#666666"))

        pwr_spark = render_mini_sparkline(self._power_history, self._power_limit, spark_width)
        text.append(pwr_spark, style=Style(color="#f39c12"))
        text.append(" PWR", style=Style(color="#666666"))

        return text
