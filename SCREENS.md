# Picomon TUI - Screen Mockups & Design

## Overview

Picomon transforms from a basic curses monitor into an incredible Textual-based TUI with:
- **Rich visualizations** - Sparklines, progress bars, color-coded metrics
- **Multiple screens** - Dashboard, GPU details, System overview, Rig Card
- **Keyboard navigation** - Vim-style keys, tab switching, quick actions
- **Shareable Rig Card** - Generate ASCII art summaries for social sharing

---

## Navigation Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  [1] Dashboard   [2] System   [3] GPU 0   [4] GPU 1  ...  [R] Rig Card     │
└─────────────────────────────────────────────────────────────────────────────┘

Keyboard Shortcuts:
  1-9      Switch to screen (1=Dashboard, 2=System, 3+=GPU details)
  Tab      Next screen
  Shift+Tab Previous screen
  r        Open Rig Card (shareable summary)
  c        Copy Rig Card to clipboard
  ?        Help overlay
  q        Quit
  j/k      Scroll down/up (in scrollable views)
  Enter    Select GPU from dashboard → GPU detail
```

---

## Screen 1: Dashboard (Default)

The main overview showing all GPUs at a glance with live metrics.

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│  PICOMON                                              ▲ 30min history │ 3s refresh  │
│  AMD GPU Monitor                                                       q quit  ? help│
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─ GPU 0 ─────────────────────────────────┐  ┌─ GPU 1 ─────────────────────────────┐│
│  │  AMD Instinct MI300X                    │  │  AMD Instinct MI300X                ││
│  │                                         │  │                                     ││
│  │  GFX   ████████████████████░░░░░  97%   │  │  GFX   ██████████████████████░  94% ││
│  │  UMC   ██░░░░░░░░░░░░░░░░░░░░░░░   7%   │  │  UMC   ███░░░░░░░░░░░░░░░░░░░   8% ││
│  │  PWR   █████████████░░░░░░░░░░░░  519W  │  │  PWR   ██████████████░░░░░░░░  533W ││
│  │        └───────────────────┘ /1000W     │  │        └───────────────────┘ /1000W ││
│  │  VRAM  ███████████████████░░░░░░  76%   │  │  VRAM  ███████████████████░░░  76%  ││
│  │        194.5 / 256.0 GB                 │  │        194.5 / 256.0 GB             ││
│  │                                         │  │                                     ││
│  │  ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃  GFX  │  │  ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇█▇▆▅▄▃▂▁  GFX ││
│  │  ▁▁▁▂▂▃▃▄▄▅▅▆▆▇▇██▇▆▅▄▃▂▁▁▂▃▄▅▆  PWR  │  │  ▁▁▂▂▃▃▄▄▅▅▆▆▇▇██▇▆▅▄▃▂▁▁▂▃▄  PWR  ││
│  └─────────────────────────────────────────┘  └─────────────────────────────────────┘│
│                                                                                      │
│  ┌─ GPU 2 ─────────────────────────────────┐  ┌─ GPU 3 ─────────────────────────────┐│
│  │  AMD Instinct MI300X                    │  │  AMD Instinct MI300X                ││
│  │                                         │  │                                     ││
│  │  GFX   ████████████████████████░  93%   │  │  GFX   ███████████████████████  97% ││
│  │  UMC   ██░░░░░░░░░░░░░░░░░░░░░░░   7%   │  │  UMC   ██░░░░░░░░░░░░░░░░░░░░   7% ││
│  │  PWR   █████████████░░░░░░░░░░░░  524W  │  │  PWR   █████████████░░░░░░░░░  519W ││
│  │        └───────────────────────┘ /1000W │  │        └───────────────────┘ /1000W ││
│  │  VRAM  ███████████████████░░░░░░  76%   │  │  VRAM  ███████████████████░░░  76%  ││
│  │        194.5 / 256.0 GB                 │  │        194.5 / 256.0 GB             ││
│  │                                         │  │                                     ││
│  │  ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃  GFX  │  │  ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇█▇▆▅▄▃▂▁  GFX ││
│  │  ▁▁▁▂▂▃▃▄▄▅▅▆▆▇▇██▇▆▅▄▃▂▁▁▂▃▄▅▆  PWR  │  │  ▁▁▂▂▃▃▄▄▅▅▆▆▇▇██▇▆▅▄▃▂▁▁▂▃▄  PWR  ││
│  └─────────────────────────────────────────┘  └─────────────────────────────────────┘│
│                                                                                      │
│  ┌─ GPU 4 ─────────────────────────────────┐  ┌─ GPU 5 ─────────────────────────────┐│
│  │  AMD Instinct MI300X                    │  │  AMD Instinct MI300X                ││
│  │                                         │  │                                     ││
│  │  GFX   ██████████████████████████ 100%  │  │  GFX   ███░░░░░░░░░░░░░░░░░░░  12% ││
│  │  UMC   █░░░░░░░░░░░░░░░░░░░░░░░░░   5%  │  │  UMC   ░░░░░░░░░░░░░░░░░░░░░░   1% ││
│  │  PWR   ██████████████░░░░░░░░░░░░  551W │  │  PWR   █████░░░░░░░░░░░░░░░░░  213W ││
│  │        └───────────────────────┘ /1000W │  │        └───────────────────┘ /1000W ││
│  │  VRAM  █████████████████████░░░░  83%   │  │  VRAM  █████████████████████░  82%  ││
│  │        211.0 / 256.0 GB                 │  │        209.3 / 256.0 GB             ││
│  │                                         │  │                                     ││
│  │  ██████████████████████████████▇▆  GFX │  │  ▁▁▁▁▁▁▁▂▃▃▂▁▁▁▁▁▂▃▄▃▂▁▁▁▁▁▁  GFX  ││
│  │  ▅▅▆▆▇▇██▇▇▆▆▅▅▄▄▃▃▂▂▃▃▄▄▅▅▆▆  PWR   │  │  ▁▁▁▁▁▁▁▂▂▂▂▁▁▁▁▁▂▂▂▂▂▁▁▁▁▁▁  PWR  ││
│  └─────────────────────────────────────────┘  └─────────────────────────────────────┘│
│                                                                                      │
├──────────────────────────────────────────────────────────────────────────────────────┤
│  TOTAL: 8 GPUs │ 4,342W / 8,000W (54%) │ 1,529 / 2,048 GB VRAM (75%) │ Avg GFX: 87% │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### Dashboard Features:
- **Compact GPU cards** - Each GPU shows key metrics at a glance
- **Color-coded bars** - Green (normal), Yellow (moderate), Red (high)
- **Mini sparklines** - Recent history preview per GPU
- **Aggregate footer** - Total power, VRAM, average utilization
- **Click/Enter to drill down** - Select a GPU for detailed view

---

## Screen 2: System Overview

Shows system-wide metrics including CPU, memory, and aggregate GPU stats.

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│  PICOMON                                              ▲ 30min history │ 3s refresh  │
│  System Overview                                                       q quit  ? help│
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─ SYSTEM ────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                                 │ │
│  │   Hostname    deep-rig-01                  OS      Ubuntu 22.04 LTS            │ │
│  │   Kernel      6.5.0-44-generic             Uptime  14 days, 3:42:17            │ │
│  │                                                                                 │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  ┌─ CPU ───────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                                 │ │
│  │   Model       AMD EPYC 9654 96-Core Processor                                  │ │
│  │   Cores       96 physical / 192 logical                                        │ │
│  │                                                                                 │ │
│  │   Usage       ██████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  34%            │ │
│  │               ▁▂▃▃▄▅▆▆▇▇██▇▇▆▆▅▅▄▄▃▃▂▂▁▁▂▂▃▃▄▄▅▅▆▆▇▇██▇▇▆▆▅▅▄▄▃▃▂▂            │ │
│  │                                                                                 │ │
│  │   Load Avg    12.34 / 8.21 / 6.45   (1m / 5m / 15m)                            │ │
│  │                                                                                 │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  ┌─ MEMORY ────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                                 │ │
│  │   RAM         ████████████████████████░░░░░░░░░░░░░░░░  512 / 1024 GB  (50%)  │ │
│  │               ▁▂▃▃▄▅▆▆▇▇██▇▇▆▆▅▅▄▄▃▃▂▂▁▁▂▂▃▃▄▄▅▅▆▆▇▇██▇▇▆▆▅▅▄▄▃▃▂▂            │ │
│  │                                                                                 │ │
│  │   Swap        ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   8 /  64 GB  (12%)   │ │
│  │                                                                                 │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  ┌─ GPU AGGREGATE ─────────────────────────────────────────────────────────────────┐ │
│  │                                                                                 │ │
│  │   Total GPUs  8 × AMD Instinct MI300X                                          │ │
│  │   Total VRAM  2,048 GB (256 GB each)                                           │ │
│  │   Total TDP   8,000 W  (1000 W each)                                           │ │
│  │                                                                                 │ │
│  │   Avg GFX     ██████████████████████████████░░░░░░░░░░░░░░░░░░  74%            │ │
│  │   Avg UMC     ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   6%            │ │
│  │   Power Draw  ████████████████████████████░░░░░░░░░░░░░░░░░░░  4,342W / 8,000W │ │
│  │   VRAM Used   █████████████████████████████████░░░░░░░░░░░░░░  1,529 / 2,048GB │ │
│  │               ▁▂▃▃▄▅▆▆▇▇██▇▇▆▆▅▅▄▄▃▃▂▂▁▁▂▂▃▃▄▄▅▅▆▆▇▇██▇▇▆▆▅▅▄▄▃▃▂▂            │ │
│  │                                                                                 │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### System Overview Features:
- **System info** - Hostname, OS, kernel, uptime
- **CPU metrics** - Model, cores, usage with sparkline history, load averages
- **Memory stats** - RAM and swap with visual bars
- **GPU aggregate** - Totals and averages across all GPUs

---

## Screen 3+: GPU Detail (One per GPU)

Deep dive into a single GPU with full metrics and detailed history.

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│  PICOMON                                              ▲ 30min history │ 3s refresh  │
│  GPU 0 Detail                                                          q quit  ? help│
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─ GPU 0: AMD Instinct MI300X ────────────────────────────────────────────────────┐ │
│  │                                                                                 │ │
│  │   Device ID     0                          HIP ID        0                     │ │
│  │   PCIe Bus      0000:03:00.0               Driver        6.7.0                 │ │
│  │   Architecture  CDNA3                      Compute Units 304                   │ │
│  │                                                                                 │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  ┌─ GFX (Graphics Engine) ─────────────────────────────────────────────────────────┐ │
│  │                                                                                 │ │
│  │   Current      ██████████████████████████████████████████████████████░░░░  97% │ │
│  │   Average      ██████████████████████████████████████████████░░░░░░░░░░░░  87% │ │
│  │   Peak         ██████████████████████████████████████████████████████████ 100% │ │
│  │                                                                                 │ │
│  │   History (30 min)                                                             │ │
│  │   100%│▁▁▁▂▃▃▄▄▅▅▆▆▇▇████▇▇▆▆▅▅▄▄▃▃▂▂▁▁▂▂▃▃▄▄▅▅▆▆▇▇████▇▇▆▆▅▅▄▄▃▃▂▂▁▁        │ │
│  │    75%│▁▁▁▂▃▃▄▄▅▅▆▆▇▇████▇▇▆▆▅▅▄▄▃▃▂▂▁▁▂▂▃▃▄▄▅▅▆▆▇▇████▇▇▆▆▅▅▄▄▃▃▂▂▁▁        │ │
│  │    50%│▁▁▁▂▃▃▄▄▅▅▆▆▇▇████▇▇▆▆▅▅▄▄▃▃▂▂▁▁▂▂▃▃▄▄▅▅▆▆▇▇████▇▇▆▆▅▅▄▄▃▃▂▂▁▁        │ │
│  │    25%│▁▁▁▂▃▃▄▄▅▅▆▆▇▇████▇▇▆▆▅▅▄▄▃▃▂▂▁▁▂▂▃▃▄▄▅▅▆▆▇▇████▇▇▆▆▅▅▄▄▃▃▂▂▁▁        │ │
│  │     0%│────────────────────────────────────────────────────────────────────     │ │
│  │        ╰──────────────────────────────────────────────────────────────╯        │ │
│  │         -30m                              -15m                          now    │ │
│  │                                                                                 │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  ┌─ Power ─────────────────────────────────┐ ┌─ VRAM ──────────────────────────────┐ │
│  │                                         │ │                                     │ │
│  │   Current  519W                         │ │   Used      194.5 GB                │ │
│  │   Limit    1000W                        │ │   Total     256.0 GB                │ │
│  │   Usage    ██████████████░░░░░░░░  52%  │ │   Usage     ██████████████████░  76%│ │
│  │                                         │ │                                     │ │
│  │   ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂       │ │   ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇█▇▆▅▄▃       │ │
│  │   ▁▁▂▂▃▃▄▄▅▅▆▆▇▇██▇▆▅▄▃▂▁▁▂▃▄▅▆       │ │   ▁▁▂▂▃▃▄▄▅▅▆▆▇▇██▇▆▅▄▃▂▁▁▂▃       │ │
│  │                                         │ │                                     │ │
│  └─────────────────────────────────────────┘ └─────────────────────────────────────┘ │
│                                                                                      │
│  ┌─ UMC (Memory Controller) ───────────────────────────────────────────────────────┐ │
│  │                                         │                                       │ │
│  │   Current  7%   Average  6%   Peak  12% │  ▁▁▂▁▁▂▁▂▁▁▂▁▂▁▁▂▁▂▁▁▂▁▂▁▁▂▁▂▁▁▂▁▂   │ │
│  │                                         │                                       │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### GPU Detail Features:
- **Full device info** - All static properties
- **Large GFX chart** - Detailed history with grid lines and time labels
- **Power & VRAM side-by-side** - Current values with mini sparklines
- **UMC stats** - Memory controller activity
- **Stats summary** - Current, average, peak values

---

## Screen R: Rig Card (Shareable Summary)

A beautiful ASCII art summary designed for sharing on social media, Discord, etc.

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│  PICOMON                                              ▲ 30min history │ 3s refresh  │
│  Rig Card                                              c copy  s save  q quit  ? help│
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  Preview:                                                                            │
│  ┌────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                                                                │  │
│  │   ╔═══════════════════════════════════════════════════════════════════════╗   │  │
│  │   ║                                                                       ║   │  │
│  │   ║   ██████╗ ██╗ ██████╗ ██████╗ ███╗   ███╗ ██████╗ ███╗   ██╗         ║   │  │
│  │   ║   ██╔══██╗██║██╔════╝██╔═══██╗████╗ ████║██╔═══██╗████╗  ██║         ║   │  │
│  │   ║   ██████╔╝██║██║     ██║   ██║██╔████╔██║██║   ██║██╔██╗ ██║         ║   │  │
│  │   ║   ██╔═══╝ ██║██║     ██║   ██║██║╚██╔╝██║██║   ██║██║╚██╗██║         ║   │  │
│  │   ║   ██║     ██║╚██████╗╚██████╔╝██║ ╚═╝ ██║╚██████╔╝██║ ╚████║         ║   │  │
│  │   ║   ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝         ║   │  │
│  │   ║                                                                       ║   │  │
│  │   ║───────────────────────────────────────────────────────────────────────║   │  │
│  │   ║                                                                       ║   │  │
│  │   ║   SYSTEM      deep-rig-01                                             ║   │  │
│  │   ║   CPU         AMD EPYC 9654 (96C/192T)                                ║   │  │
│  │   ║   RAM         1,024 GB DDR5                                           ║   │  │
│  │   ║                                                                       ║   │  │
│  │   ║───────────────────────────────────────────────────────────────────────║   │  │
│  │   ║                                                                       ║   │  │
│  │   ║   GPU CLUSTER                                                         ║   │  │
│  │   ║   ────────────────────────────────────────────────────                ║   │  │
│  │   ║   8 × AMD Instinct MI300X                                             ║   │  │
│  │   ║                                                                       ║   │  │
│  │   ║   VRAM        2,048 GB (256 GB × 8)                                   ║   │  │
│  │   ║   TDP         8,000 W  (1,000 W × 8)                                  ║   │  │
│  │   ║                                                                       ║   │  │
│  │   ║───────────────────────────────────────────────────────────────────────║   │  │
│  │   ║                                                                       ║   │  │
│  │   ║   LIVE STATS                                                          ║   │  │
│  │   ║   ────────────────────────────────────────────────────                ║   │  │
│  │   ║   GFX Load    ████████████████████████████░░░░░░░░░░░░  74%           ║   │  │
│  │   ║   Power Draw  ████████████████████████████░░░░░░░░░░░░  4,342W        ║   │  │
│  │   ║   VRAM Used   █████████████████████████████████░░░░░░░  1,529 GB      ║   │  │
│  │   ║                                                                       ║   │  │
│  │   ║═══════════════════════════════════════════════════════════════════════║   │  │
│  │   ║   Generated by picomon │ github.com/your-username/picomon            ║   │  │
│  │   ╚═══════════════════════════════════════════════════════════════════════╝   │  │
│  │                                                                                │  │
│  └────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
│  Press 'c' to copy to clipboard, 's' to save as text file                           │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### Rig Card Features:
- **ASCII art logo** - Eye-catching branding
- **System summary** - Hostname, CPU, RAM
- **GPU cluster overview** - Count, model, total VRAM/TDP
- **Live stats** - Current utilization bars
- **One-click copy** - For pasting to Discord, Twitter, forums
- **Save to file** - Export as .txt for archiving

---

## Alternative Rig Card: Compact Version

For smaller embeds and quick sharing:

```
╭───────────────────────────────────────────╮
│             P I C O M O N                 │
│─────────────────────────────────────────────│
│  deep-rig-01                              │
│  AMD EPYC 9654 │ 1,024 GB RAM             │
│─────────────────────────────────────────────│
│  8 × AMD Instinct MI300X                  │
│  2,048 GB VRAM │ 8,000 W TDP              │
│─────────────────────────────────────────────│
│  GFX  ████████████████████░░░░░░░░  74%   │
│  PWR  ████████████████████░░░░░░░░  4.3kW │
│  VRAM █████████████████████████░░░  1.5TB │
╰───────────────────────────────────────────╯
```

---

## Help Overlay (?)

Accessible from any screen with `?`:

```
┌─────────────────────────────────────────────────────────────────────┐
│                          PICOMON HELP                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  NAVIGATION                                                         │
│  ───────────────────────────────────────────                       │
│  1             Dashboard (GPU overview)                             │
│  2             System overview                                      │
│  3-9           GPU detail pages                                     │
│  Tab           Next screen                                          │
│  Shift+Tab     Previous screen                                      │
│  r             Rig Card (shareable summary)                         │
│                                                                     │
│  ACTIONS                                                            │
│  ───────────────────────────────────────────                       │
│  c             Copy Rig Card to clipboard                           │
│  s             Save Rig Card to file                                │
│  j / k         Scroll down / up                                     │
│  Enter         Select / drill down                                  │
│                                                                     │
│  GENERAL                                                            │
│  ───────────────────────────────────────────                       │
│  ?             Toggle this help                                     │
│  q             Quit                                                 │
│  Ctrl+C        Force quit                                           │
│                                                                     │
│  Press any key to close                                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Color Scheme

### Default Theme (Dark)
- **Background**: #1a1a2e (deep navy)
- **Primary**: #e94560 (vibrant red/pink)
- **Secondary**: #0f3460 (dark blue)
- **Accent**: #16c79a (teal green)
- **Text**: #eaeaea (off-white)
- **Muted**: #666666 (gray)

### Metric Colors
- **GFX bar**: Gradient from #16c79a (green) → #f39c12 (orange) → #e94560 (red)
- **Power bar**: #f39c12 (orange) base, red when > 80%
- **VRAM bar**: #3498db (blue), red when > 90%
- **UMC bar**: #9b59b6 (purple)

### Thresholds
- **Low** (0-50%): Green #16c79a
- **Medium** (50-80%): Yellow/Orange #f39c12
- **High** (80-100%): Red #e94560

---

## Responsive Layout

### Large Terminal (160+ cols)
- 4 GPUs per row in dashboard
- Full-width charts in detail view

### Medium Terminal (100-160 cols)
- 2 GPUs per row (as shown in mockups)
- Standard layout

### Small Terminal (80-100 cols)
- 1 GPU per row in dashboard
- Stacked layout in detail view

### Minimum (80 cols × 24 rows)
- Compact mode with abbreviated labels
- Single-column layout

---

## Implementation Notes

### Textual Components
- **App**: Main application with screen management
- **Screens**: Dashboard, SystemOverview, GPUDetail, RigCard
- **Widgets**: GPUCard, MetricBar, Sparkline, StatBox
- **Themes**: Dark (default), Light mode option

### Data Flow
1. Background worker polls `amd-smi` every N seconds
2. Updates shared state (GPUHistory dict)
3. Reactive UI updates via Textual's message system
4. All screens reflect latest data automatically

### Performance
- Efficient rendering with Textual's virtual DOM
- Minimal redraws using reactive properties
- History data structure with O(1) append/prune

---

## File Structure

```
src/picomon/
├── __init__.py
├── config.py          # Configuration (existing)
├── history.py         # GPU history data (existing)
├── smi.py            # AMD SMI interface (existing)
├── monitor.py        # Entry point (updated)
├── app.py            # NEW: Textual App class
├── screens/          # NEW: Screen definitions
│   ├── __init__.py
│   ├── dashboard.py
│   ├── system.py
│   ├── gpu_detail.py
│   └── rig_card.py
├── widgets/          # NEW: Reusable widgets
│   ├── __init__.py
│   ├── gpu_card.py
│   ├── metric_bar.py
│   ├── sparkline.py
│   └── stat_box.py
├── styles/           # NEW: CSS styles
│   └── app.tcss
└── system_info.py    # NEW: System metrics (CPU, RAM)
```
