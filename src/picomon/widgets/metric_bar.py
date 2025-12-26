"""Metric bar widget for displaying progress-style metrics."""

from __future__ import annotations

from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text
from rich.style import Style


class MetricBar(Widget):
    """A horizontal bar showing a metric value as a percentage."""

    DEFAULT_CSS = """
    MetricBar {
        height: 1;
        min-width: 20;
    }
    """

    value: reactive[float] = reactive(0.0)
    max_value: reactive[float] = reactive(100.0)
    label: reactive[str] = reactive("")
    value_text: reactive[str] = reactive("")
    show_percentage: reactive[bool] = reactive(True)
    warning_threshold: reactive[float] = reactive(0.7)
    danger_threshold: reactive[float] = reactive(0.9)

    def __init__(
        self,
        value: float = 0.0,
        max_value: float = 100.0,
        *,
        label: str = "",
        value_text: str = "",
        show_percentage: bool = True,
        warning_threshold: float = 0.7,
        danger_threshold: float = 0.9,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.value = value
        self.max_value = max_value
        self.label = label
        self.value_text = value_text
        self.show_percentage = show_percentage
        self.warning_threshold = warning_threshold
        self.danger_threshold = danger_threshold

    @property
    def percentage(self) -> float:
        """Get the value as a percentage of max."""
        if self.max_value <= 0:
            return 0.0
        return min(100.0, max(0.0, (self.value / self.max_value) * 100))

    @property
    def ratio(self) -> float:
        """Get the value as a ratio (0-1)."""
        return self.percentage / 100.0

    def _get_bar_color(self) -> str:
        """Get the color based on the current value."""
        ratio = self.ratio
        if ratio >= self.danger_threshold:
            return "#e74c3c"  # Red
        elif ratio >= self.warning_threshold:
            return "#f39c12"  # Orange
        else:
            return "#16c79a"  # Green

    def render(self) -> Text:
        """Render the metric bar."""
        width = self.size.width

        # Calculate space for label and value text
        label_part = f"{self.label}  " if self.label else ""

        if self.value_text:
            value_part = f" {self.value_text}"
        elif self.show_percentage:
            value_part = f" {self.percentage:5.1f}%"
        else:
            value_part = ""

        bar_width = width - len(label_part) - len(value_part)
        if bar_width < 5:
            bar_width = 5

        # Calculate filled portion
        filled = int(bar_width * self.ratio)
        empty = bar_width - filled

        # Build the bar
        bar_color = self._get_bar_color()
        filled_char = "\u2588"  # Full block
        empty_char = "\u2591"  # Light shade

        text = Text()

        if label_part:
            text.append(label_part, style=Style(color="#888888"))

        text.append(filled_char * filled, style=Style(color=bar_color))
        text.append(empty_char * empty, style=Style(color="#333333"))

        if value_part:
            text.append(value_part, style=Style(color="#eaeaea"))

        return text


class CompactMetricBar(Widget):
    """A more compact metric bar with value on the same line."""

    DEFAULT_CSS = """
    CompactMetricBar {
        height: 1;
        min-width: 30;
    }
    """

    value: reactive[float] = reactive(0.0)
    max_value: reactive[float] = reactive(100.0)
    label: reactive[str] = reactive("")
    unit: reactive[str] = reactive("")
    bar_width: reactive[int] = reactive(20)

    def __init__(
        self,
        value: float = 0.0,
        max_value: float = 100.0,
        *,
        label: str = "",
        unit: str = "",
        bar_width: int = 20,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.value = value
        self.max_value = max_value
        self.label = label
        self.unit = unit
        self.bar_width = bar_width

    @property
    def ratio(self) -> float:
        """Get the value as a ratio (0-1)."""
        if self.max_value <= 0:
            return 0.0
        return min(1.0, max(0.0, self.value / self.max_value))

    def _get_bar_color(self, ratio: float) -> str:
        """Get the color based on the ratio."""
        if ratio >= 0.9:
            return "#e74c3c"
        elif ratio >= 0.7:
            return "#f39c12"
        else:
            return "#16c79a"

    def render(self) -> Text:
        """Render the compact metric bar."""
        text = Text()

        # Label
        if self.label:
            text.append(f"{self.label:5s} ", style=Style(color="#888888"))

        # Bar
        ratio = self.ratio
        filled = int(self.bar_width * ratio)
        empty = self.bar_width - filled
        bar_color = self._get_bar_color(ratio)

        text.append("\u2588" * filled, style=Style(color=bar_color))
        text.append("\u2591" * empty, style=Style(color="#333333"))

        # Value
        pct = ratio * 100
        if self.unit:
            text.append(f" {self.value:6.1f}{self.unit}", style=Style(color="#eaeaea"))
        else:
            text.append(f" {pct:5.1f}%", style=Style(color="#eaeaea"))

        return text
