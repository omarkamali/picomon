"""Main Textual application for Picomon."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Footer
from textual.containers import Container
from textual.binding import Binding
from rich.text import Text
from rich.style import Style

from .screens.dashboard import DashboardScreen
from .screens.system import SystemScreen
from .screens.gpu_detail import GPUDetailScreen
from .screens.rig_card import RigCardScreen
from .system_info import SystemInfo, SystemMetrics, load_system_info, update_system_metrics

if TYPE_CHECKING:
    from .providers.base import GPUHistory
    from .config import PicomonConfig


class HelpScreen(Screen):
    """Help overlay screen."""

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("q", "dismiss", "Close"),
        ("?", "dismiss", "Close"),
    ]

    CSS = """
    HelpScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #help-container {
        width: 70;
        height: auto;
        max-height: 80%;
        padding: 1 2;
        background: #16213e;
        border: double #e94560;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(id="help-container")

    def on_mount(self) -> None:
        container = self.query_one("#help-container", Static)
        text = Text()

        text.append("PICOMON HELP\n", style=Style(color="#e94560", bold=True))
        text.append("\u2500" * 66 + "\n\n", style=Style(color="#0f3460"))

        text.append("NAVIGATION\n", style=Style(color="#888888", bold=True))
        text.append("\u2500" * 40 + "\n", style=Style(color="#0f3460"))

        keys = [
            ("1", "Dashboard (GPU overview)"),
            ("2", "System overview"),
            ("3-9", "GPU detail pages"),
            ("Tab", "Next screen"),
            ("Shift+Tab", "Previous screen"),
            ("r", "Rig Card (shareable summary)"),
            ("Escape", "Go back / Close"),
        ]

        for key, desc in keys:
            text.append(f"  {key:14}", style=Style(color="#16c79a"))
            text.append(f"{desc}\n", style=Style(color="#eaeaea"))

        text.append("\n")
        text.append("ACTIONS\n", style=Style(color="#888888", bold=True))
        text.append("\u2500" * 40 + "\n", style=Style(color="#0f3460"))

        actions = [
            ("c", "Copy Rig Card to clipboard"),
            ("s", "Save Rig Card to file"),
            ("m", "Toggle Rig Card mode"),
            ("Enter", "Select / drill down"),
        ]

        for key, desc in actions:
            text.append(f"  {key:14}", style=Style(color="#16c79a"))
            text.append(f"{desc}\n", style=Style(color="#eaeaea"))

        text.append("\n")
        text.append("GENERAL\n", style=Style(color="#888888", bold=True))
        text.append("\u2500" * 40 + "\n", style=Style(color="#0f3460"))

        general = [
            ("?", "Toggle this help"),
            ("q", "Quit"),
            ("Ctrl+C", "Force quit"),
        ]

        for key, desc in general:
            text.append(f"  {key:14}", style=Style(color="#16c79a"))
            text.append(f"{desc}\n", style=Style(color="#eaeaea"))

        text.append("\n")
        text.append("\u2500" * 66 + "\n", style=Style(color="#0f3460"))
        text.append("Press any key to close", style=Style(color="#666666"))

        container.update(text)

    def on_key(self, event) -> None:
        """Handle any key to close."""
        self.app.pop_screen()

    def action_dismiss(self) -> None:
        """Dismiss the help screen."""
        self.app.pop_screen()


class PicomonApp(App):
    """Main Textual application for Picomon."""

    TITLE = "Picomon"
    SUB_TITLE = "GPU Monitor"

    CSS_PATH = Path(__file__).parent / "styles" / "app.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("?", "help", "Help", show=True),
        Binding("1", "screen_dashboard", "Dashboard", show=True),
        Binding("2", "screen_system", "System", show=True),
        Binding("r", "screen_rig_card", "Rig Card", show=True),
        Binding("3", "screen_gpu_0", "GPU 0", show=False),
        Binding("4", "screen_gpu_1", "GPU 1", show=False),
        Binding("5", "screen_gpu_2", "GPU 2", show=False),
        Binding("6", "screen_gpu_3", "GPU 3", show=False),
        Binding("7", "screen_gpu_4", "GPU 4", show=False),
        Binding("8", "screen_gpu_5", "GPU 5", show=False),
        Binding("9", "screen_gpu_6", "GPU 6", show=False),
    ]

    def __init__(
        self,
        config: "PicomonConfig",
        gpus: dict[int, "GPUHistory"],
        tick_callback,
    ) -> None:
        super().__init__()
        self._config = config
        self._gpus = gpus
        self._tick_callback = tick_callback
        self._sys_info: SystemInfo | None = None
        self._sys_metrics: SystemMetrics | None = None
        self._update_task: asyncio.Task | None = None

    def on_mount(self) -> None:
        """Handle app mount."""
        # Load system info
        try:
            self._sys_info = load_system_info()
            self._sys_metrics = SystemMetrics(max_points=self._config.max_points)
            update_system_metrics(self._sys_metrics)
        except Exception:
            pass

        # Install screens
        self._install_screens()

        # Push the dashboard as the initial screen
        self.push_screen("dashboard")

        # Start the update loop
        self._update_task = asyncio.create_task(self._update_loop())

    def _install_screens(self) -> None:
        """Install all screens."""
        # Dashboard
        dashboard = DashboardScreen(
            gpus=self._gpus,
            history_minutes=self._config.history_minutes,
            update_interval=self._config.update_interval,
        )
        self.install_screen(dashboard, name="dashboard")

        # System
        system = SystemScreen(
            sys_info=self._sys_info,
            sys_metrics=self._sys_metrics,
            gpus=self._gpus,
        )
        self.install_screen(system, name="system")

        # Rig Card
        rig_card = RigCardScreen(
            sys_info=self._sys_info,
            sys_metrics=self._sys_metrics,
            gpus=self._gpus,
        )
        self.install_screen(rig_card, name="rig_card")

        # Help
        self.install_screen(HelpScreen(), name="help")

        # GPU detail screens
        sorted_gpus = sorted(
            self._gpus.keys(),
            key=lambda idx: (
                self._gpus[idx].hip_id if self._gpus[idx].hip_id is not None else idx,
                idx,
            ),
        )
        for i, gpu_idx in enumerate(sorted_gpus):
            detail = GPUDetailScreen(gpu_idx=gpu_idx, gpu_history=self._gpus[gpu_idx])
            self.install_screen(detail, name=f"gpu_detail_{gpu_idx}")

    async def _update_loop(self) -> None:
        """Background task to update metrics."""
        while True:
            try:
                await asyncio.sleep(self._config.update_interval)

                # Update GPU metrics
                if self._tick_callback:
                    self._tick_callback()

                # Update system metrics
                if self._sys_metrics:
                    update_system_metrics(self._sys_metrics)

                # Refresh the current screen
                current_screen = self.screen
                if hasattr(current_screen, "refresh_metrics"):
                    current_screen.refresh_metrics()
                elif hasattr(current_screen, "refresh_data"):
                    current_screen.refresh_data()

            except asyncio.CancelledError:
                break
            except Exception:
                pass

    def action_quit(self) -> None:
        """Quit the application."""
        if self._update_task:
            self._update_task.cancel()
        self.exit()

    def action_help(self) -> None:
        """Show help screen."""
        self.push_screen("help")

    def action_screen_dashboard(self) -> None:
        """Switch to dashboard."""
        self.switch_screen("dashboard")

    def action_screen_system(self) -> None:
        """Switch to system screen."""
        if self.screen.name == "system":
            return
        self.push_screen("system")

    def action_screen_rig_card(self) -> None:
        """Switch to rig card screen."""
        if self.screen.name == "rig_card":
            return
        self.push_screen("rig_card")

    def _action_screen_gpu(self, gpu_num: int) -> None:
        """Switch to a GPU detail screen."""
        sorted_gpus = sorted(
            self._gpus.keys(),
            key=lambda idx: (
                self._gpus[idx].hip_id if self._gpus[idx].hip_id is not None else idx,
                idx,
            ),
        )
        if gpu_num < len(sorted_gpus):
            gpu_idx = sorted_gpus[gpu_num]
            screen_name = f"gpu_detail_{gpu_idx}"
            if self.screen.name == screen_name:
                return
            self.push_screen(screen_name)

    def action_screen_gpu_0(self) -> None:
        """Switch to GPU 0 detail."""
        self._action_screen_gpu(0)

    def action_screen_gpu_1(self) -> None:
        """Switch to GPU 1 detail."""
        self._action_screen_gpu(1)

    def action_screen_gpu_2(self) -> None:
        """Switch to GPU 2 detail."""
        self._action_screen_gpu(2)

    def action_screen_gpu_3(self) -> None:
        """Switch to GPU 3 detail."""
        self._action_screen_gpu(3)

    def action_screen_gpu_4(self) -> None:
        """Switch to GPU 4 detail."""
        self._action_screen_gpu(4)

    def action_screen_gpu_5(self) -> None:
        """Switch to GPU 5 detail."""
        self._action_screen_gpu(5)

    def action_screen_gpu_6(self) -> None:
        """Switch to GPU 6 detail."""
        self._action_screen_gpu(6)


def run_textual_app(
    config: "PicomonConfig",
    gpus: dict[int, "GPUHistory"],
    tick_callback,
) -> None:
    """Run the Textual app."""
    app = PicomonApp(config, gpus, tick_callback)
    app.run()
