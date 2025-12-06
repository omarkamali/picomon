---
layout: default
title: picomon
---

# picomon

A tiny curses dashboard for AMD GPUs powered by `amd-smi`.

<div class="terminal">
  <div class="terminal-header">
    <span class="dot red"></span>
    <span class="dot yellow"></span>
    <span class="dot green"></span>
    <span class="title">omarkamali@picomon</span>
  </div>
  <pre>
┌──────────────────────────────────────────┐  ┌──────────────────────────────────────────┐
│ GPU 0  GFX  42%  UMC  21%                │  │ GPU 1  GFX  78%  UMC  66%                │
│ PWR 135/250W (54%)  VRAM 10.0/16.0GB 62% │  │ PWR 210/250W (84%)  VRAM 14.5/16.0GB 90% │
│                                          │  │                                          │
│ GFX ▁▁▂▄▄▅▆▆▇█▇▆▅▄▃▂▁                     │  │ GFX ▃▄▅▆▇██▇▆▅▄▂▁▁▂▃▅▆                   │
│ PWR ▁▁▁▂▂▃▄▄▅▆▇██▇▆▅▄▂▁                   │  │ PWR ▂▃▃▄▄▅▆▇██▇▆▅▄▃▂▂▃                   │
│ VRM ▁▁▂▂▃▄▄▅▆▆▇███▇▆▅▄▃▂                   │  │ VRM ▂▃▄▅▆▆▇███▇▆▅▄▃▂▂▃                   │
└──────────────────────────────────────────┘  └──────────────────────────────────────────┘
  </pre>
</div>

## Install

```shell
pip install picomon
```

## Run

```shell
picomon --update-interval 2 --history-minutes 15
```

## Configure

Use the CLI flags (they map to the `PicomonConfig` dataclass) to tweak polling rate,
history window, and AMD SMI timeouts. picomon only needs `amd-smi` on your PATH and
an ANSI-compatible terminal.

<style>
.terminal { font-family: "Fira Code", "SFMono-Regular", Menlo, Consolas, monospace; background:#111; color:#d9d9d9; border-radius:12px; box-shadow:0 10px 40px rgba(0,0,0,0.35); margin:2rem 0; }
.terminal-header { display:flex; align-items:center; gap:8px; padding:0.6rem 1rem; background:#1f1f1f; border-top-left-radius:12px; border-top-right-radius:12px; }
.dot { width:10px; height:10px; border-radius:50%; display:inline-block; }
.dot.red { background:#ff5f56; }
.dot.yellow { background:#ffbd2e; }
.dot.green { background:#27c93f; }
.terminal .title { margin-left:auto; font-size:0.85rem; color:#7d7d7d; }
.terminal pre { margin:0; padding:1.25rem; font-size:0.9rem; overflow-x:auto; }
body { font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background:#f9fafb; color:#111; }
</style>
