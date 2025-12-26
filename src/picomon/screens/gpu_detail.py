"""GPU detail screen using proper Textual widgets."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.screen import Screen
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.widgets import Static, Footer
from rich.text import Text
from rich.style import Style

if TYPE_CHECKING:
    from ..providers.base import GPUHistory


# Unicode blocks for sparklines
BLOCKS = " ▁▂▃▄▅▆▇█"


def render_sparkline(data: list[float], max_val: float, width: int = 50) -> str:
    """Render a single-row sparkline."""
    if not data:
        return " " * width

    if len(data) > width:
        step = len(data) / width
        data = [data[int(i * step)] for i in range(width)]
    elif len(data) < width:
        padding = width - len(data)
        data = [0.0] * padding + data

    if max_val <= 0:
        max_val = 1.0

    result = []
    nb = len(BLOCKS) - 1

    for val in data:
        normalized = max(0.0, min(1.0, val / max_val))
        level = int(normalized * nb)
        result.append(BLOCKS[level])

    return "".join(result)


def render_large_chart(data: list[float], max_val: float, width: int = 50, height: int = 6) -> list[str]:
    """Render a multi-row chart.

    Returns:
        List of strings, one per row (from top to bottom).
    """
    if not data:
        return [" " * width for _ in range(height)]

    if len(data) > width:
        step = len(data) / width
        data = [data[int(i * step)] for i in range(width)]
    elif len(data) < width:
        padding = width - len(data)
        data = [0.0] * padding + data

    if max_val <= 0:
        max_val = 1.0

    rows = []
    for row_idx in range(height):
        row_bottom = (height - row_idx - 1) / height
        row_top = (height - row_idx) / height

        row_chars = []
        for val in data:
            normalized = max(0.0, min(1.0, val / max_val))

            if normalized <= row_bottom:
                row_chars.append(" ")
            elif normalized >= row_top:
                row_chars.append(BLOCKS[8])
            else:
                fraction = (normalized - row_bottom) / (row_top - row_bottom)
                level = int(fraction * 8)
                row_chars.append(BLOCKS[level])

        rows.append("".join(row_chars))

    return rows


class SectionBox(Container):
    """A container with a styled border and title."""

    DEFAULT_CSS = """
    SectionBox {
        height: auto;
        margin: 1;
        padding: 1;
        background: #16213e;
        border: solid #0f3460;
    }
    """

    def __init__(self, title: str, **kwargs):
        super().__init__(**kwargs)
        self.border_title = title


class InfoRow(Static):
    """A row displaying label: value."""

    DEFAULT_CSS = """
    InfoRow {
        height: 1;
    }
    """

    def __init__(self, label: str, value: str, **kwargs):
        super().__init__(**kwargs)
        self._label = label
        self._value = value

    def set_value(self, value: str):
        self._value = value
        self.refresh()

    def render(self) -> Text:
        text = Text()
        text.append(f"{self._label:14s}", style=Style(color="#888888"))
        text.append(self._value, style=Style(color="#eaeaea"))
        return text


class MetricBar(Static):
    """A metric with progress bar."""

    DEFAULT_CSS = """
    MetricBar {
        height: auto;
        margin: 0 0 1 0;
    }
    """

    def __init__(self, label: str, value: float = 0, max_value: float = 100, unit: str = "%", **kwargs):
        super().__init__(**kwargs)
        self._label = label
        self._value = value
        self._max_value = max_value
        self._unit = unit

    def update_value(self, value: float, max_value: float | None = None):
        self._value = value
        if max_value is not None:
            self._max_value = max_value
        self.refresh()

    def render(self) -> Text:
        text = Text()
        pct = (self._value / self._max_value * 100) if self._max_value > 0 else 0
        bar_width = 40
        filled = int(bar_width * pct / 100)
        empty = bar_width - filled

        if pct >= 90:
            color = "#e74c3c"
        elif pct >= 70:
            color = "#f39c12"
        else:
            color = "#16c79a"

        text.append(f"{self._label:12s}", style=Style(color="#888888"))
        text.append("\u2588" * filled, style=Style(color=color))
        text.append("\u2591" * empty, style=Style(color="#333333"))

        if self._unit == "%":
            text.append(f"  {pct:5.1f}%", style=Style(color="#eaeaea"))
        else:
            text.append(f"  {self._value:.1f} {self._unit}", style=Style(color="#eaeaea"))

        return text


class ChartDisplay(Static):
    """A large chart display with history."""

    DEFAULT_CSS = """
    ChartDisplay {
        height: auto;
        margin: 1 0;
    }
    """

    def __init__(
        self,
        label: str,
        data: list[float] | None = None,
        max_value: float = 100,
        color: str = "#16c79a",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._label = label
        self._data = data or []
        self._max_value = max_value
        self._color = color
        self._current = 0.0
        self._average = 0.0
        self._peak = 0.0

    def update_data(self, data: list[float], max_value: float | None = None):
        self._data = data
        if max_value is not None:
            self._max_value = max_value
        if data:
            self._current = data[-1]
            self._average = sum(data) / len(data)
            self._peak = max(data)
        self.refresh()

    def render(self) -> Text:
        text = Text()

        # Stats row
        text.append("Current  ", style=Style(color="#888888"))
        text.append(f"{self._current:5.1f}%", style=Style(color="#eaeaea"))
        text.append("    Average  ", style=Style(color="#888888"))
        text.append(f"{self._average:5.1f}%", style=Style(color="#eaeaea"))
        text.append("    Peak  ", style=Style(color="#888888"))
        text.append(f"{self._peak:5.1f}%\n\n", style=Style(color="#eaeaea"))

        # Progress bars
        bar_width = 45

        # Current bar
        pct = (self._current / self._max_value * 100) if self._max_value > 0 else 0
        filled = int(bar_width * pct / 100)
        empty = bar_width - filled
        if pct >= 90:
            color = "#e74c3c"
        elif pct >= 70:
            color = "#f39c12"
        else:
            color = self._color
        text.append("Current  ", style=Style(color="#888888"))
        text.append("\u2588" * filled, style=Style(color=color))
        text.append("\u2591" * empty, style=Style(color="#333333"))
        text.append(f" {pct:5.1f}%\n", style=Style(color="#eaeaea"))

        # Average bar
        pct = (self._average / self._max_value * 100) if self._max_value > 0 else 0
        filled = int(bar_width * pct / 100)
        empty = bar_width - filled
        text.append("Average  ", style=Style(color="#888888"))
        text.append("\u2588" * filled, style=Style(color=self._color))
        text.append("\u2591" * empty, style=Style(color="#333333"))
        text.append(f" {pct:5.1f}%\n", style=Style(color="#eaeaea"))

        # Peak bar
        pct = (self._peak / self._max_value * 100) if self._max_value > 0 else 0
        filled = int(bar_width * pct / 100)
        empty = bar_width - filled
        text.append("Peak     ", style=Style(color="#888888"))
        text.append("\u2588" * filled, style=Style(color="#e94560"))
        text.append("\u2591" * empty, style=Style(color="#333333"))
        text.append(f" {pct:5.1f}%\n", style=Style(color="#eaeaea"))

        # Chart
        text.append("\nHistory\n", style=Style(color="#888888"))
        chart_rows = render_large_chart(self._data, self._max_value, 55, 5)
        labels = ["100%", " 75%", " 50%", " 25%", "  0%"]
        for label, row in zip(labels, chart_rows):
            text.append(f"{label}\u2502", style=Style(color="#666666"))
            text.append(row, style=Style(color=self._color))
            text.append("\n")

        return text


class SparklineDisplay(Static):
    """A sparkline display."""

    DEFAULT_CSS = """
    SparklineDisplay {
        height: 2;
        margin: 1 0 0 0;
    }
    """

    def __init__(
        self,
        label: str = "",
        data: list[float] | None = None,
        max_value: float = 100,
        color: str = "#16c79a",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._label = label
        self._data = data or []
        self._max_value = max_value
        self._color = color

    def update_data(self, data: list[float], max_value: float | None = None):
        self._data = data
        if max_value is not None:
            self._max_value = max_value
        self.refresh()

    def render(self) -> Text:
        text = Text()
        spark = render_sparkline(self._data, self._max_value, 50)
        text.append(spark, style=Style(color=self._color))
        if self._label:
            text.append(f" {self._label}", style=Style(color="#666666"))
        return text


class GPUDetailHeader(Static):
    """Header for GPU detail screen."""

    DEFAULT_CSS = """
    GPUDetailHeader {
        dock: top;
        height: 3;
        background: #16213e;
        border-bottom: solid #e94560;
        padding: 0 2;
    }
    """

    def __init__(self, gpu_idx: int, gpu_name: str = "GPU"):
        super().__init__()
        self._gpu_idx = gpu_idx
        self._gpu_name = gpu_name

    def render(self) -> Text:
        text = Text()
        text.append("PICOMON", style=Style(color="#e94560", bold=True))
        text.append(f"  GPU {self._gpu_idx}: {self._gpu_name}\n", style=Style(color="#888888"))
        text.append("Press 1 or ESC to return to Dashboard", style=Style(color="#666666"))
        return text


class GPUDetailScreen(Screen):
    """Detailed view for a single GPU."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("?", "help", "Help"),
        ("r", "rig_card", "Rig Card"),
        ("1", "dashboard", "Dashboard"),
        ("2", "system", "System"),
        ("escape", "back", "Back"),
    ]

    CSS = """
    GPUDetailScreen {
        background: #1a1a2e;
    }

    #detail-scroll {
        padding: 0 1;
    }

    .side-by-side {
        height: auto;
        layout: horizontal;
    }

    .side-by-side > SectionBox {
        width: 1fr;
    }
    """

    def __init__(
        self,
        gpu_idx: int,
        gpu_history: "GPUHistory | None" = None,
    ) -> None:
        super().__init__()
        self._gpu_idx = gpu_idx
        self._gpu_history = gpu_history

    def compose(self):
        """Compose the GPU detail screen."""
        gpu_name = self._gpu_history.name if self._gpu_history and self._gpu_history.name else "GPU"
        yield GPUDetailHeader(self._gpu_idx, gpu_name)

        with ScrollableContainer(id="detail-scroll"):
            # GPU Info section
            with SectionBox(f"GPU {self._gpu_idx}", id="info-box"):
                yield InfoRow("Device ID", str(self._gpu_idx), id="info-device")

                vendor = self._gpu_history.vendor if self._gpu_history else "Unknown"
                yield InfoRow("Vendor", vendor, id="info-vendor")

                if self._gpu_history and self._gpu_history.sort_index is not None:
                    sort_label = "HIP ID" if vendor == "AMD" else "Sort ID"
                    yield InfoRow(sort_label, str(self._gpu_history.sort_index), id="info-sort")

                vram_gb = self._gpu_history.vram_total_mb / 1024 if self._gpu_history else 0
                yield InfoRow("VRAM Total", f"{vram_gb:.1f} GB", id="info-vram")

                power_limit = self._gpu_history.power_limit_w if self._gpu_history else 0
                yield InfoRow("Power Limit", f"{power_limit:.0f} W", id="info-power")

            # GFX section with large chart
            with SectionBox("GPU Utilization", id="gfx-box"):
                yield ChartDisplay(
                    "GFX",
                    data=list(self._gpu_history.gfx) if self._gpu_history else [],
                    max_value=100,
                    color="#16c79a",
                    id="gfx-chart",
                )

            # Power and VRAM side by side
            with Horizontal(classes="side-by-side"):
                with SectionBox("Power", id="power-box"):
                    yield MetricBar(
                        "Current",
                        value=0,
                        max_value=self._gpu_history.power_limit_w if self._gpu_history else 100,
                        unit="W",
                        id="power-current",
                    )
                    yield SparklineDisplay(
                        data=list(self._gpu_history.power_w) if self._gpu_history else [],
                        max_value=self._gpu_history.power_limit_w if self._gpu_history else 100,
                        color="#f39c12",
                        id="power-spark",
                    )

                with SectionBox("VRAM", id="vram-box"):
                    yield MetricBar(
                        "Used",
                        value=0,
                        max_value=self._gpu_history.vram_total_mb / 1024 if self._gpu_history else 1,
                        unit="GB",
                        id="vram-current",
                    )
                    yield SparklineDisplay(
                        data=[v / 1024 for v in self._gpu_history.vram_used_mb] if self._gpu_history else [],
                        max_value=self._gpu_history.vram_total_mb / 1024 if self._gpu_history else 1,
                        color="#3498db",
                        id="vram-spark",
                    )

            # UMC section
            with SectionBox("Memory Controller (UMC)", id="umc-box"):
                umc_data = list(self._gpu_history.umc) if self._gpu_history else []
                current = umc_data[-1] if umc_data else 0
                average = sum(umc_data) / len(umc_data) if umc_data else 0
                peak = max(umc_data) if umc_data else 0

                yield InfoRow("Current", f"{current:.1f}%", id="umc-current")
                yield InfoRow("Average", f"{average:.1f}%", id="umc-average")
                yield InfoRow("Peak", f"{peak:.1f}%", id="umc-peak")
                yield SparklineDisplay(
                    data=umc_data,
                    max_value=100,
                    color="#9b59b6",
                    id="umc-spark",
                )

        yield Footer()

    def on_mount(self) -> None:
        """Handle mount event."""
        self.refresh_data()

    def refresh_data(self) -> None:
        """Refresh all data."""
        if not self._gpu_history:
            return

        # Update GFX chart
        try:
            gfx_chart = self.query_one("#gfx-chart", ChartDisplay)
            gfx_chart.update_data(list(self._gpu_history.gfx), 100)
        except Exception:
            pass

        # Update power
        try:
            power = self._gpu_history.power_w[-1] if self._gpu_history.power_w else 0
            self.query_one("#power-current", MetricBar).update_value(
                power, self._gpu_history.power_limit_w
            )
            self.query_one("#power-spark", SparklineDisplay).update_data(
                list(self._gpu_history.power_w), self._gpu_history.power_limit_w
            )
        except Exception:
            pass

        # Update VRAM
        try:
            vram = self._gpu_history.vram_used_mb[-1] / 1024 if self._gpu_history.vram_used_mb else 0
            vram_total = self._gpu_history.vram_total_mb / 1024
            self.query_one("#vram-current", MetricBar).update_value(vram, vram_total)
            self.query_one("#vram-spark", SparklineDisplay).update_data(
                [v / 1024 for v in self._gpu_history.vram_used_mb], vram_total
            )
        except Exception:
            pass

        # Update UMC
        try:
            umc_data = list(self._gpu_history.umc)
            if umc_data:
                self.query_one("#umc-current", InfoRow).set_value(f"{umc_data[-1]:.1f}%")
                self.query_one("#umc-average", InfoRow).set_value(f"{sum(umc_data)/len(umc_data):.1f}%")
                self.query_one("#umc-peak", InfoRow).set_value(f"{max(umc_data):.1f}%")
                self.query_one("#umc-spark", SparklineDisplay).update_data(umc_data, 100)
        except Exception:
            pass

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_help(self) -> None:
        """Show help."""
        self.app.push_screen("help")

    def action_rig_card(self) -> None:
        """Show rig card."""
        self.app.push_screen("rig_card")

    def action_dashboard(self) -> None:
        """Go to dashboard."""
        self.app.switch_screen("dashboard")

    def action_system(self) -> None:
        """Go to system."""
        self.app.push_screen("system")

    def action_back(self) -> None:
        """Go back."""
        self.app.pop_screen()
