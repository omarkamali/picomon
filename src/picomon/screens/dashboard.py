"""Dashboard screen showing all GPUs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.screen import Screen
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer, Grid
from textual.widgets import Static, Footer
from textual.reactive import reactive
from rich.text import Text
from rich.style import Style

from ..widgets.gpu_card import GPUCard

if TYPE_CHECKING:
    from ..providers.base import GPUHistory


class DashboardHeader(Static):
    """Header widget for the dashboard."""

    DEFAULT_CSS = """
    DashboardHeader {
        dock: top;
        height: 3;
        background: #16213e;
        border-bottom: solid #e94560;
        padding: 0 2;
    }
    """

    def __init__(self, history_minutes: int = 30, update_interval: float = 3.0) -> None:
        super().__init__()
        self.history_minutes = history_minutes
        self.update_interval = update_interval

    def render(self) -> Text:
        text = Text()
        text.append("PICOMON", style=Style(color="#e94560", bold=True))
        text.append("  GPU Monitor\n", style=Style(color="#888888"))
        text.append(
            f"\u25b2 {self.history_minutes}min history \u2502 {self.update_interval}s refresh",
            style=Style(color="#666666"),
        )
        return text


class DashboardFooter(Static):
    """Footer widget showing aggregate stats."""

    DEFAULT_CSS = """
    DashboardFooter {
        dock: bottom;
        height: 1;
        background: #16213e;
        border-top: solid #0f3460;
        padding: 0 2;
    }
    """

    total_gpus: reactive[int] = reactive(0)
    total_power: reactive[float] = reactive(0.0)
    max_power: reactive[float] = reactive(0.0)
    total_vram: reactive[float] = reactive(0.0)
    max_vram: reactive[float] = reactive(0.0)
    avg_gfx: reactive[float] = reactive(0.0)

    def render(self) -> Text:
        text = Text()

        pwr_pct = (self.total_power / self.max_power * 100) if self.max_power > 0 else 0
        vram_pct = (self.total_vram / self.max_vram * 100) if self.max_vram > 0 else 0

        text.append(f"TOTAL: {self.total_gpus} GPUs", style=Style(color="#888888"))
        text.append(" \u2502 ", style=Style(color="#333333"))

        # Power color
        if pwr_pct >= 90:
            pwr_color = "#e74c3c"
        elif pwr_pct >= 70:
            pwr_color = "#f39c12"
        else:
            pwr_color = "#16c79a"
        text.append(f"{self.total_power:.0f}/{self.max_power:.0f}W ({pwr_pct:.0f}%)", style=Style(color=pwr_color))

        text.append(" \u2502 ", style=Style(color="#333333"))

        # VRAM color
        if vram_pct >= 90:
            vram_color = "#e74c3c"
        elif vram_pct >= 70:
            vram_color = "#f39c12"
        else:
            vram_color = "#3498db"
        vram_tb = self.total_vram / (1024 * 1024)
        max_vram_tb = self.max_vram / (1024 * 1024)
        text.append(f"{vram_tb:.2f}/{max_vram_tb:.2f} TB VRAM ({vram_pct:.0f}%)", style=Style(color=vram_color))

        text.append(" \u2502 ", style=Style(color="#333333"))

        # Avg GFX color
        if self.avg_gfx >= 90:
            gfx_color = "#e74c3c"
        elif self.avg_gfx >= 70:
            gfx_color = "#f39c12"
        else:
            gfx_color = "#16c79a"
        text.append(f"Avg GFX: {self.avg_gfx:.0f}%", style=Style(color=gfx_color))

        return text


class DashboardScreen(Screen):
    """Main dashboard screen showing all GPUs."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("?", "help", "Help"),
        ("r", "rig_card", "Rig Card"),
        ("s", "system", "System"),
        ("1", "dashboard", "Dashboard"),
        ("2", "system", "System"),
    ]

    CSS = """
    DashboardScreen {
        background: #1a1a2e;
    }

    #gpu-grid {
        padding: 1;
    }

    #gpu-grid > GPUCard {
        width: 1fr;
    }
    """

    def __init__(
        self,
        gpus: dict[int, "GPUHistory"] | None = None,
        history_minutes: int = 30,
        update_interval: float = 3.0,
    ) -> None:
        super().__init__()
        self._gpus = gpus or {}
        self._history_minutes = history_minutes
        self._update_interval = update_interval
        self._gpu_cards: dict[int, GPUCard] = {}
        self._footer: DashboardFooter | None = None

    def compose(self):
        """Compose the dashboard layout."""
        yield DashboardHeader(self._history_minutes, self._update_interval)

        # Create GPU grid
        with ScrollableContainer(id="gpu-grid"):
            with Grid(id="card-grid"):
                # Sort GPUs by HIP ID
                sorted_gpus = sorted(
                    self._gpus.items(),
                    key=lambda x: (x[1].hip_id if x[1].hip_id is not None else x[0], x[0]),
                )
                for gpu_idx, hist in sorted_gpus:
                    gpu_name = hist.name if hist.name else "GPU"
                    card = GPUCard(gpu_idx, gpu_name, id=f"gpu-card-{gpu_idx}")
                    self._gpu_cards[gpu_idx] = card
                    yield card

        self._footer = DashboardFooter()
        yield self._footer

        yield Footer()

    def on_mount(self) -> None:
        """Handle mount event."""
        # Style the grid
        grid = self.query_one("#card-grid", Grid)
        # Determine columns based on GPU count and terminal width
        num_gpus = len(self._gpus)
        if num_gpus <= 2:
            grid.styles.grid_size_columns = 1
        elif num_gpus <= 4:
            grid.styles.grid_size_columns = 2
        else:
            grid.styles.grid_size_columns = 2
        grid.styles.grid_gutter_horizontal = 1
        grid.styles.grid_gutter_vertical = 1

        # Initial update
        self.refresh_metrics()

    def refresh_metrics(self) -> None:
        """Refresh all GPU metrics."""
        total_power = 0.0
        max_power = 0.0
        total_vram = 0.0
        max_vram = 0.0
        total_gfx = 0.0

        for gpu_idx, hist in self._gpus.items():
            card = self._gpu_cards.get(gpu_idx)
            if card is None:
                continue

            # Get latest values
            gfx = hist.gfx[-1] if hist.gfx else 0.0
            umc = hist.umc[-1] if hist.umc else 0.0
            power = hist.power_w[-1] if hist.power_w else 0.0
            vram_used = hist.vram_used_mb[-1] if hist.vram_used_mb else 0.0

            card.update_metrics(
                gfx=gfx,
                umc=umc,
                power=power,
                power_limit=hist.power_limit_w,
                vram_used=vram_used,
                vram_total=hist.vram_total_mb,
                gfx_history=list(hist.gfx),
                power_history=list(hist.power_w),
            )

            # Accumulate totals
            total_power += power
            max_power += hist.power_limit_w
            total_vram += vram_used
            max_vram += hist.vram_total_mb
            total_gfx += gfx

        # Update footer
        if self._footer:
            self._footer.total_gpus = len(self._gpus)
            self._footer.total_power = total_power
            self._footer.max_power = max_power
            self._footer.total_vram = total_vram
            self._footer.max_vram = max_vram
            self._footer.avg_gfx = total_gfx / len(self._gpus) if self._gpus else 0.0

    def on_gpu_card_selected(self, message: GPUCard.Selected) -> None:
        """Handle GPU card selection."""
        self.app.push_screen(f"gpu_detail_{message.gpu_idx}")

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_help(self) -> None:
        """Show help."""
        self.app.push_screen("help")

    def action_rig_card(self) -> None:
        """Show rig card."""
        self.app.push_screen("rig_card")

    def action_system(self) -> None:
        """Show system overview."""
        self.app.push_screen("system")

    def action_dashboard(self) -> None:
        """Already on dashboard."""
        pass
