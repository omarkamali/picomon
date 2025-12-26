#!/usr/bin/env python3
"""
Generate properly aligned ASCII art for the picomon website.

This script ensures all box-drawing characters are perfectly aligned by:
1. Using a helper function that pads content to exact widths
2. Verifying all lines in each block have identical character counts

Usage:
    python generate_ascii_art.py

The output can be copied into docs/index.html, wrapping content in appropriate
<span class="t-*"> tags for coloring.

Note: The website uses CDNFonts for JetBrains Mono instead of Google Fonts,
because Google Fonts subsets exclude box-drawing characters (U+2500-257F).
"""


def line(content: str, width: int, left: str = "│", right: str = "│") -> str:
    """Create a bordered line with exact width (excluding borders).

    Args:
        content: The text content for the line
        width: The inner width (excluding border characters)
        left: Left border character
        right: Right border character

    Returns:
        A string of exactly (width + 2) characters
    """
    if len(content) < width:
        content = content + " " * (width - len(content))
    elif len(content) > width:
        content = content[:width]
    return f"{left}{content}{right}"


def verify_block(name: str, lines: list[str]) -> None:
    """Verify all lines in a block have the same length."""
    lengths = set(len(l) for l in lines)
    if len(lengths) == 1:
        print(f"  ✓ {name}: {lengths.pop()} chars per line")
    else:
        print(f"  ✗ {name}: MISALIGNED - {lengths}")
        for i, l in enumerate(lines):
            print(f"      Line {i}: {len(l)} chars")


def generate_hero_terminal() -> list[str]:
    """Generate the main hero terminal with two GPU cards side by side.

    Each GPU box has inner width of 32 characters.
    Total line width: 69 characters (34 + 1 space + 34)
    """
    W = 32  # Inner width of each GPU box
    lines = []

    # Header (no box)
    lines.append("PICOMON  GPU Monitor")
    lines.append("▲ 30min history │ 3.0s refresh")
    lines.append("")

    # Top border
    lines.append(f"┌{'─'*W}┐ ┌{'─'*W}┐")

    # GPU headers
    lines.append(f"{line(' GPU 0  Apple M3 Max GPU', W)} {line(' GPU 1  RTX 4090', W)}")

    # Empty line
    lines.append(f"{line('', W)} {line('', W)}")

    # Progress bars (18 chars each: filled + empty)
    lines.append(f"{line(' GFX  ██████████░░░░░░░░ 52%', W)} {line(' GFX  ██████████████░░░░ 78%', W)}")
    lines.append(f"{line(' UMC  ████░░░░░░░░░░░░░░ 18%', W)} {line(' UMC  ██████████░░░░░░░░ 56%', W)}")
    lines.append(f"{line(' PWR  ██░░░░░░░░░░░░░░░░  6W', W)} {line(' PWR  ████████████░░░░░░ 320W', W)}")
    lines.append(f"{line(' VRAM ██████████████░░░░ 80%', W)} {line(' VRAM ██████████░░░░░░░░ 52%', W)}")

    # Empty line
    lines.append(f"{line('', W)} {line('', W)}")

    # Sparklines (18 chars + label)
    lines.append(f"{line(' ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄ GFX', W)} {line(' ▂▃▅▆▇█████▇▆▅▄▃▂▁▂ GFX', W)}")
    lines.append(f"{line(' ▁▁▂▂▃▄▅▆▇█▇▆▅▄▃▂▁▁ PWR', W)} {line(' ▂▃▄▅▆▇████▇▆▅▄▃▂▂▃ PWR', W)}")

    # Bottom border
    lines.append(f"└{'─'*W}┘ └{'─'*W}┘")

    lines.append("")
    lines.append("TOTAL: 2 GPUs │ 326/450W │ 20.5/40.0 GB │ Avg GFX: 65%")

    return lines


def generate_dashboard_preview() -> list[str]:
    """Generate the dashboard screen preview (single GPU card).

    Inner width: 27 characters
    Total line width: 29 characters
    """
    W = 27
    lines = []

    lines.append(f"┌{'─'*W}┐")
    lines.append(line(" GPU 0  Apple M3 Max", W))
    lines.append(line("", W))
    lines.append(line(" GFX  ████████░░░░  52%", W))
    lines.append(line(" UMC  ███░░░░░░░░░  18%", W))
    lines.append(line(" PWR  ██░░░░░░░░░░   6W", W))
    lines.append(line(" VRAM ██████████░░  80%", W))
    lines.append(line("", W))
    lines.append(line(" ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁ GFX", W))
    lines.append(line(" ▁▁▂▂▃▄▅▆▇█▇▆▅▄ PWR", W))
    lines.append(f"└{'─'*W}┘")

    return lines


def generate_system_preview() -> list[str]:
    """Generate the system screen preview.

    Inner width: 27 characters
    Total line width: 29 characters
    """
    W = 27
    lines = []

    # System info box
    lines.append(f"┌─ SYSTEM {'─'*(W-9)}┐")
    lines.append(line(" Hostname   my-workstation", W))
    lines.append(line(" OS         Ubuntu 24.04", W))
    lines.append(line(" Kernel     6.8.0-generic", W))
    lines.append(line(" Uptime     4d 12h 33m", W))
    lines.append(f"└{'─'*W}┘")

    # CPU info box
    lines.append(f"┌─ CPU {'─'*(W-6)}┐")
    lines.append(line(" AMD Ryzen 9 7950X", W))
    lines.append(line(" 16 cores / 32 threads", W))
    lines.append(line(" Usage ████████░░░░ 42%", W))
    lines.append(line(" ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄", W))
    lines.append(f"└{'─'*W}┘")

    return lines


def generate_gpu_detail_preview() -> list[str]:
    """Generate the GPU detail screen preview.

    Inner width: 27 characters
    Total line width: 29 characters
    """
    W = 27
    lines = []

    # Header: "─ GPU 0: RTX 4090 " = 18 chars, need 9 more dashes
    lines.append(f"┌─ GPU 0: RTX 4090 {'─'*(W-18)}┐")
    lines.append(line("", W))
    lines.append(line(" Utilization", W))
    lines.append(line(" ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇█", W))
    lines.append(line("", W))
    lines.append(line(" Power Draw", W))
    lines.append(line(" ▂▃▄▅▆▇████▇▆▅▄▃▂▂▃▄▅▆▇", W))
    lines.append(line("", W))
    lines.append(line(" Temp: 72°C  Fan: 65%", W))
    lines.append(line(" Clock: 2520 MHz", W))
    lines.append(f"└{'─'*W}┘")

    return lines


def generate_rigcard_small_preview() -> list[str]:
    """Generate the small rig card preview.

    Inner width: 27 characters
    Total line width: 29 characters
    """
    W = 27
    lines = []

    lines.append(f"╔{'═'*W}╗")
    lines.append(line("     P I C O M O N", W, "║", "║"))
    lines.append(line("    GPU Monitoring TUI", W, "║", "║"))
    lines.append(f"╠{'═'*W}╣")
    lines.append(line(" SYSTEM  my-workstation", W, "║", "║"))
    lines.append(line(" CPU     Ryzen 9 7950X", W, "║", "║"))
    lines.append(line(" RAM     128 GB", W, "║", "║"))
    lines.append(f"╠{'═'*W}╣")
    lines.append(line(" 2 × RTX 4090", W, "║", "║"))
    lines.append(line(" 48 GB VRAM │ 900W TDP", W, "║", "║"))
    lines.append(f"╚{'═'*W}╝")

    return lines


def generate_rigcard_full() -> list[str]:
    """Generate the full rig card for the CTA section.

    Inner width: 58 characters
    Total line width: 60 characters
    """
    W = 58
    lines = []

    lines.append(f"╔{'═'*W}╗")
    lines.append(line("                  P  I  C  O  M  O  N", W, "║", "║"))
    lines.append(line("                   GPU Monitoring TUI", W, "║", "║"))
    lines.append(f"╠{'═'*W}╣")
    lines.append(line("  SYSTEM      my-workstation", W, "║", "║"))
    lines.append(line("  CPU         AMD Ryzen 9 7950X", W, "║", "║"))
    lines.append(line("  RAM         128 GB", W, "║", "║"))
    lines.append(f"╠{'═'*W}╣")
    lines.append(line("  GPU CLUSTER", W, "║", "║"))
    lines.append(line("  ────────────────────────────────────────", W, "║", "║"))
    lines.append(line("  2 × NVIDIA RTX 4090", W, "║", "║"))
    lines.append(line("  VRAM        48 GB (24 GB × 2)", W, "║", "║"))
    lines.append(line("  TDP         900 W (450 W × 2)", W, "║", "║"))
    lines.append(f"╠{'═'*W}╣")
    lines.append(line("  LIVE STATS", W, "║", "║"))
    lines.append(line("  GPU Load    ████████████████░░░░░░░░░░░░░░  52.3%", W, "║", "║"))
    lines.append(line("  Power Draw  ██████████░░░░░░░░░░░░░░░░░░░░   380W", W, "║", "║"))
    lines.append(line("  VRAM Used   ████████████░░░░░░░░░░░░░░░░░░    20GB", W, "║", "║"))
    lines.append(f"╠{'═'*W}╣")
    lines.append(line("  Generated by picomon │ 2025-12-26 12:00", W, "║", "║"))
    lines.append(f"╚{'═'*W}╝")

    return lines


def main():
    print("=" * 70)
    print("PICOMON WEBSITE ASCII ART GENERATOR")
    print("=" * 70)
    print()

    blocks = [
        ("Hero Terminal", generate_hero_terminal()),
        ("Dashboard Preview", generate_dashboard_preview()),
        ("System Preview", generate_system_preview()),
        ("GPU Detail Preview", generate_gpu_detail_preview()),
        ("Rig Card Small", generate_rigcard_small_preview()),
        ("Rig Card Full", generate_rigcard_full()),
    ]

    for name, lines in blocks:
        print(f"\n{'='*70}")
        print(f"{name.upper()}")
        print("=" * 70)
        for l in lines:
            print(l)

    # Verification
    print(f"\n{'='*70}")
    print("VERIFICATION")
    print("=" * 70)

    for name, lines in blocks:
        # Only check lines that are part of boxes (start with box characters)
        box_lines = [l for l in lines if l and l[0] in "┌└│╔╚║╠"]
        if box_lines:
            verify_block(name, box_lines)

    print()
    print("Note: Copy the output above into docs/index.html")
    print("Wrap colored content in <span class='t-*'> tags:")
    print("  t-accent  = red (PICOMON, GPU 0, etc.)")
    print("  t-cyan    = cyan (progress bars, sparklines)")
    print("  t-orange  = orange (power bars)")
    print("  t-blue    = blue (VRAM bars)")
    print("  t-muted   = gray (labels)")
    print("  t-text    = white (values)")
    print("  t-border  = dark blue (box characters)")


if __name__ == "__main__":
    main()
