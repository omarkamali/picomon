"""Stat box widget for displaying key statistics."""

from __future__ import annotations

from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text
from rich.style import Style


class StatBox(Widget):
    """A box displaying a labeled statistic."""

    DEFAULT_CSS = """
    StatBox {
        height: 3;
        min-width: 12;
        padding: 0 1;
        background: #1f3055;
        border: solid #0f3460;
    }
    """

    label: reactive[str] = reactive("")
    value: reactive[str] = reactive("")
    sublabel: reactive[str] = reactive("")

    def __init__(
        self,
        label: str = "",
        value: str = "",
        sublabel: str = "",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.label = label
        self.value = value
        self.sublabel = sublabel

    def render(self) -> Text:
        """Render the stat box."""
        text = Text()

        # Label line
        text.append(f"{self.label}\n", style=Style(color="#888888"))

        # Value line
        text.append(f"{self.value}\n", style=Style(color="#eaeaea", bold=True))

        # Sublabel line (if any)
        if self.sublabel:
            text.append(self.sublabel, style=Style(color="#666666"))

        return text


class InlineStatBox(Widget):
    """An inline stat display with label and value on same line."""

    DEFAULT_CSS = """
    InlineStatBox {
        height: 1;
        min-width: 20;
    }
    """

    label: reactive[str] = reactive("")
    value: reactive[str] = reactive("")

    def __init__(
        self,
        label: str = "",
        value: str = "",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.label = label
        self.value = value

    def render(self) -> Text:
        """Render the inline stat."""
        text = Text()
        text.append(f"{self.label}: ", style=Style(color="#888888"))
        text.append(self.value, style=Style(color="#eaeaea"))
        return text
