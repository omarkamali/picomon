"""Sparkline widget for displaying time-series data."""

from __future__ import annotations

from typing import Sequence

from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text


# Unicode block characters for sparklines (8 levels)
BLOCKS = " ▁▂▃▄▅▆▇█"


class Sparkline(Widget):
    """A sparkline chart widget that displays time-series data."""

    DEFAULT_CSS = """
    Sparkline {
        height: 2;
        min-width: 10;
    }
    """

    data: reactive[tuple[float, ...]] = reactive(())
    max_value: reactive[float] = reactive(100.0)
    min_value: reactive[float] = reactive(0.0)
    label: reactive[str] = reactive("")
    show_label: reactive[bool] = reactive(True)

    def __init__(
        self,
        data: Sequence[float] | None = None,
        *,
        max_value: float = 100.0,
        min_value: float = 0.0,
        label: str = "",
        show_label: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.data = tuple(data) if data else ()
        self.max_value = max_value
        self.min_value = min_value
        self.label = label
        self.show_label = show_label

    def update_data(self, data: Sequence[float]) -> None:
        """Update the sparkline data."""
        self.data = tuple(data)

    def _render_sparkline(self, width: int) -> tuple[str, str]:
        """Render sparkline as two rows of Unicode blocks.

        Returns:
            Tuple of (top_row, bottom_row) strings.
        """
        if not self.data:
            return (" " * width, " " * width)

        # Sample data to fit width
        data = list(self.data)
        if len(data) > width:
            # Downsample: take evenly spaced samples
            step = len(data) / width
            data = [data[int(i * step)] for i in range(width)]
        elif len(data) < width:
            # Pad with spaces on the left
            padding = width - len(data)
            data = [self.min_value] * padding + data

        # Normalize values to 0-1 range
        value_range = self.max_value - self.min_value
        if value_range <= 0:
            value_range = 1.0

        normalized = [
            max(0.0, min(1.0, (v - self.min_value) / value_range)) for v in data
        ]

        # Build two rows: top (50-100%) and bottom (0-50%)
        top_row = []
        bottom_row = []
        nb = len(BLOCKS) - 1  # 8 levels

        for val in normalized:
            if val <= 0.5:
                # Only bottom row has content
                level = int(val * 2 * nb)
                top_row.append(" ")
                bottom_row.append(BLOCKS[level])
            else:
                # Both rows have content
                bottom_row.append(BLOCKS[nb])  # Full block
                top_level = int((val - 0.5) * 2 * nb)
                top_row.append(BLOCKS[top_level])

        return ("".join(top_row), "".join(bottom_row))

    def render(self) -> Text:
        """Render the sparkline."""
        width = self.size.width
        if self.show_label and self.label:
            label_width = len(self.label) + 1
            chart_width = max(1, width - label_width)
        else:
            label_width = 0
            chart_width = width

        top_row, bottom_row = self._render_sparkline(chart_width)

        # Build output with optional label
        lines = []
        if self.show_label and self.label:
            lines.append(f"{self.label} {top_row}")
            lines.append(f"{' ' * len(self.label)} {bottom_row}")
        else:
            lines.append(top_row)
            lines.append(bottom_row)

        return Text("\n".join(lines))


class MiniSparkline(Widget):
    """A compact single-row sparkline."""

    DEFAULT_CSS = """
    MiniSparkline {
        height: 1;
        min-width: 10;
    }
    """

    data: reactive[tuple[float, ...]] = reactive(())
    max_value: reactive[float] = reactive(100.0)
    min_value: reactive[float] = reactive(0.0)

    def __init__(
        self,
        data: Sequence[float] | None = None,
        *,
        max_value: float = 100.0,
        min_value: float = 0.0,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.data = tuple(data) if data else ()
        self.max_value = max_value
        self.min_value = min_value

    def update_data(self, data: Sequence[float]) -> None:
        """Update the sparkline data."""
        self.data = tuple(data)

    def render(self) -> Text:
        """Render the sparkline."""
        width = self.size.width
        if not self.data:
            return Text(" " * width)

        # Sample data to fit width
        data = list(self.data)
        if len(data) > width:
            step = len(data) / width
            data = [data[int(i * step)] for i in range(width)]
        elif len(data) < width:
            padding = width - len(data)
            data = [self.min_value] * padding + data

        # Normalize and render
        value_range = self.max_value - self.min_value
        if value_range <= 0:
            value_range = 1.0

        result = []
        nb = len(BLOCKS) - 1

        for val in data:
            normalized = max(0.0, min(1.0, (val - self.min_value) / value_range))
            level = int(normalized * nb)
            result.append(BLOCKS[level])

        return Text("".join(result))
