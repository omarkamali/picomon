"""System overview screen using proper Textual widgets."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Static, Footer, Label, ProgressBar
from textual.reactive import reactive
from rich.text import Text
from rich.style import Style

if TYPE_CHECKING:
    from ..providers.base import GPUHistory
    from ..system_info import SystemInfo, SystemMetrics


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


class MetricDisplay(Static):
    """A styled metric display with label, bar, and value."""

    DEFAULT_CSS = """
    MetricDisplay {
        height: auto;
        margin: 0 0 1 0;
    }

    MetricDisplay .metric-row {
        height: 1;
    }

    MetricDisplay .metric-label {
        width: 12;
        color: #888888;
    }

    MetricDisplay .metric-bar {
        width: 1fr;
        min-width: 20;
    }

    MetricDisplay .metric-value {
        width: auto;
        min-width: 20;
        text-align: right;
        color: #eaeaea;
    }

    MetricDisplay .sparkline {
        height: 1;
        margin-left: 12;
        color: #16c79a;
    }
    """

    def __init__(
        self,
        label: str,
        value: float = 0,
        max_value: float = 100,
        unit: str = "%",
        show_sparkline: bool = False,
        sparkline_data: list[float] | None = None,
        sparkline_color: str = "#16c79a",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.label = label
        self._value = value
        self._max_value = max_value
        self._unit = unit
        self._show_sparkline = show_sparkline
        self._sparkline_data = sparkline_data or []
        self._sparkline_color = sparkline_color

    def update_value(
        self,
        value: float,
        max_value: float | None = None,
        sparkline_data: list[float] | None = None,
    ):
        """Update the metric value."""
        self._value = value
        if max_value is not None:
            self._max_value = max_value
        if sparkline_data is not None:
            self._sparkline_data = sparkline_data
        self.refresh()

    def render(self) -> Text:
        text = Text()

        # Calculate percentage and bar
        pct = (self._value / self._max_value * 100) if self._max_value > 0 else 0
        bar_width = 35
        filled = int(bar_width * pct / 100)
        empty = bar_width - filled

        # Color based on value
        if pct >= 90:
            color = "#e74c3c"
        elif pct >= 70:
            color = "#f39c12"
        else:
            color = "#16c79a"

        # Render
        text.append(f"{self.label:12s}", style=Style(color="#888888"))
        text.append("\u2588" * filled, style=Style(color=color))
        text.append("\u2591" * empty, style=Style(color="#333333"))

        # Value display
        if self._unit == "%":
            text.append(f"  {pct:5.1f}%", style=Style(color="#eaeaea"))
        else:
            text.append(
                f"  {self._value:.1f} / {self._max_value:.1f} {self._unit} ({pct:.0f}%)",
                style=Style(color="#eaeaea"),
            )

        # Sparkline if enabled
        if self._show_sparkline and self._sparkline_data:
            text.append("\n")
            text.append(" " * 12, style=Style(color="#888888"))
            spark = render_sparkline(self._sparkline_data, self._max_value, 40)
            text.append(spark, style=Style(color=self._sparkline_color))

        return text


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

    SectionBox > .section-title {
        color: #e94560;
        text-style: bold;
        margin-bottom: 1;
    }

    SectionBox > .section-content {
        height: auto;
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


class SystemHeader(Static):
    """Header for the system screen."""

    DEFAULT_CSS = """
    SystemHeader {
        dock: top;
        height: 3;
        background: #16213e;
        border-bottom: solid #e94560;
        padding: 0 2;
    }
    """

    def render(self) -> Text:
        text = Text()
        text.append("PICOMON", style=Style(color="#e94560", bold=True))
        text.append("  System Overview\n", style=Style(color="#888888"))
        text.append("Press 1 or ESC to return to Dashboard", style=Style(color="#666666"))
        return text


class SystemScreen(Screen):
    """System overview screen with CPU, RAM, and aggregate GPU stats."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("?", "help", "Help"),
        ("r", "rig_card", "Rig Card"),
        ("1", "dashboard", "Dashboard"),
        ("2", "system", "System"),
        ("escape", "dashboard", "Back"),
    ]

    CSS = """
    SystemScreen {
        background: #1a1a2e;
    }

    #system-scroll {
        padding: 0 1;
    }
    """

    def __init__(
        self,
        sys_info: "SystemInfo | None" = None,
        sys_metrics: "SystemMetrics | None" = None,
        gpus: dict[int, "GPUHistory"] | None = None,
    ) -> None:
        super().__init__()
        self._sys_info = sys_info
        self._sys_metrics = sys_metrics
        self._gpus = gpus or {}

    def compose(self):
        """Compose the system screen."""
        yield SystemHeader()

        with ScrollableContainer(id="system-scroll"):
            # System info section
            with SectionBox("SYSTEM", id="system-box"):
                yield InfoRow("Hostname", self._sys_info.hostname if self._sys_info else "Unknown", id="info-hostname")
                yield InfoRow("OS", self._sys_info.os_name if self._sys_info else "Unknown", id="info-os")
                yield InfoRow("Kernel", self._sys_info.kernel if self._sys_info else "Unknown", id="info-kernel")
                yield InfoRow("Uptime", self._sys_info.uptime_str if self._sys_info else "Unknown", id="info-uptime")

            # CPU section
            with SectionBox("CPU", id="cpu-box"):
                cpu_model = self._sys_info.cpu_model if self._sys_info else "Unknown"
                if len(cpu_model) > 50:
                    cpu_model = cpu_model[:47] + "..."
                yield InfoRow("Model", cpu_model, id="cpu-model")

                cores = "Unknown"
                if self._sys_info:
                    cores = f"{self._sys_info.cpu_cores_physical} physical / {self._sys_info.cpu_cores_logical} logical"
                yield InfoRow("Cores", cores, id="cpu-cores")

                yield MetricDisplay(
                    "Usage",
                    value=self._sys_metrics.cpu_percent if self._sys_metrics else 0,
                    max_value=100,
                    unit="%",
                    show_sparkline=True,
                    sparkline_data=list(self._sys_metrics.cpu_history) if self._sys_metrics else [],
                    id="cpu-usage",
                )

                load = "0.0 / 0.0 / 0.0"
                if self._sys_metrics:
                    load = f"{self._sys_metrics.load_1m:.2f} / {self._sys_metrics.load_5m:.2f} / {self._sys_metrics.load_15m:.2f}"
                yield InfoRow("Load Avg", f"{load}  (1m / 5m / 15m)", id="cpu-load")

            # Memory section
            with SectionBox("MEMORY", id="memory-box"):
                yield MetricDisplay(
                    "RAM",
                    value=self._sys_metrics.ram_used_gb if self._sys_metrics else 0,
                    max_value=self._sys_metrics.ram_total_gb if self._sys_metrics else 1,
                    unit="GB",
                    show_sparkline=True,
                    sparkline_data=list(self._sys_metrics.ram_history) if self._sys_metrics else [],
                    sparkline_color="#3498db",
                    id="mem-ram",
                )

                yield MetricDisplay(
                    "Swap",
                    value=self._sys_metrics.swap_used_gb if self._sys_metrics else 0,
                    max_value=self._sys_metrics.swap_total_gb if self._sys_metrics else 1,
                    unit="GB",
                    show_sparkline=False,
                    id="mem-swap",
                )

            # GPU Cluster section
            with SectionBox("GPU CLUSTER", id="gpu-box"):
                if self._gpus:
                    num_gpus = len(self._gpus)
                    first_gpu = next(iter(self._gpus.values()), None)
                    gpu_name = first_gpu.name if first_gpu and first_gpu.name else "GPU"
                    yield InfoRow("Total GPUs", f"{num_gpus} \u00d7 {gpu_name}", id="gpu-count")

                    total_vram = sum(h.vram_total_mb for h in self._gpus.values()) / 1024
                    per_vram = total_vram / num_gpus
                    yield InfoRow("Total VRAM", f"{total_vram:.0f} GB ({per_vram:.0f} GB \u00d7 {num_gpus})", id="gpu-vram")

                    total_tdp = sum(h.power_limit_w for h in self._gpus.values())
                    per_tdp = total_tdp / num_gpus
                    yield InfoRow("Total TDP", f"{total_tdp:.0f} W ({per_tdp:.0f} W \u00d7 {num_gpus})", id="gpu-tdp")

                    yield Static("", id="gpu-spacer")

                    yield MetricDisplay("Avg GFX", id="gpu-gfx")
                    yield MetricDisplay("Avg UMC", id="gpu-umc")
                    yield MetricDisplay("Power", id="gpu-power")
                    yield MetricDisplay("VRAM", id="gpu-vram-used")
                else:
                    yield InfoRow("Status", "No GPUs detected", id="gpu-none")

        yield Footer()

    def on_mount(self) -> None:
        """Handle mount event."""
        self.refresh_data()

    def refresh_data(self) -> None:
        """Refresh all data."""
        # Update system info
        if self._sys_info:
            try:
                self.query_one("#info-uptime", InfoRow).set_value(self._sys_info.uptime_str)
            except Exception:
                pass

        # Update CPU metrics
        if self._sys_metrics:
            try:
                cpu_usage = self.query_one("#cpu-usage", MetricDisplay)
                cpu_usage.update_value(
                    self._sys_metrics.cpu_percent,
                    sparkline_data=list(self._sys_metrics.cpu_history),
                )
            except Exception:
                pass

            try:
                load_row = self.query_one("#cpu-load", InfoRow)
                load = f"{self._sys_metrics.load_1m:.2f} / {self._sys_metrics.load_5m:.2f} / {self._sys_metrics.load_15m:.2f}"
                load_row.set_value(f"{load}  (1m / 5m / 15m)")
            except Exception:
                pass

            # Update memory
            try:
                ram = self.query_one("#mem-ram", MetricDisplay)
                ram.update_value(
                    self._sys_metrics.ram_used_gb,
                    self._sys_metrics.ram_total_gb,
                    list(self._sys_metrics.ram_history),
                )
            except Exception:
                pass

            try:
                swap = self.query_one("#mem-swap", MetricDisplay)
                swap.update_value(
                    self._sys_metrics.swap_used_gb,
                    self._sys_metrics.swap_total_gb,
                )
            except Exception:
                pass

        # Update GPU metrics
        if self._gpus:
            num_gpus = len(self._gpus)
            total_vram = sum(h.vram_total_mb for h in self._gpus.values())
            total_tdp = sum(h.power_limit_w for h in self._gpus.values())

            avg_gfx = sum(h.gfx[-1] if h.gfx else 0 for h in self._gpus.values()) / num_gpus
            avg_umc = sum(h.umc[-1] if h.umc else 0 for h in self._gpus.values()) / num_gpus
            total_power = sum(h.power_w[-1] if h.power_w else 0 for h in self._gpus.values())
            total_vram_used = sum(h.vram_used_mb[-1] if h.vram_used_mb else 0 for h in self._gpus.values())

            try:
                self.query_one("#gpu-gfx", MetricDisplay).update_value(avg_gfx, 100)
            except Exception:
                pass

            try:
                self.query_one("#gpu-umc", MetricDisplay).update_value(avg_umc, 100)
            except Exception:
                pass

            try:
                pwr = self.query_one("#gpu-power", MetricDisplay)
                pwr._unit = "W"
                pwr.update_value(total_power, total_tdp)
            except Exception:
                pass

            try:
                vram = self.query_one("#gpu-vram-used", MetricDisplay)
                vram._unit = "GB"
                vram.update_value(total_vram_used / 1024, total_vram / 1024)
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
        self.app.pop_screen()

    def action_system(self) -> None:
        """Already on system."""
        pass
