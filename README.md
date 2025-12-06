# picomon

picomon is a tiny terminal dashboard for monitoring AMD GPUs via `amd-smi`. It polls basic metrics (gfx activity, memory usage, and power) and renders them as sparklines inside a curses UI so you can keep an eye on accelerators without launching a full GUI stack. 

Homepage: <https://omarkamali.github.io/picomon/>

## Why?

I like nvtop but the asserts kept crashing it on some AMD devices. picomon is a lightweight alternative that just polls metrics and renders them as sparklines, trading off ironclad checks for more reliability.

It hasn't been tested on all AMD GPUs. If it fails to run on your GPU, please open a new issue using [this template](https://github.com/omarkamali/picomon/issues/new?assignees=&labels=bug&template=bug_report.md&title=%5BBug%5D).

## Requirements

- Python 3.9 or newer
- The `amd-smi` CLI available on your PATH (if your GPU is properly setup then you already have this)
- An ANSI-compatible terminal for the curses UI

## Installation

```shell
pip install picomon
```

Development installs (for local hacking) can use editable mode:

```shell
pip install -e '.[dev]'
```

## Usage

After installation, run the CLI:

```shell
picomon
```

Key bindings:
- `q` to quit

Common flags:
- `--update-interval` (seconds between refreshes, default 3)
- `--history-minutes` (rolling window to retain, default 30)
- `--static-timeout` / `--metric-timeout` (seconds to wait for `amd-smi` responses)

These correspond to the `PicomonConfig` dataclass, so you can also import and reuse
picomon as a library:

```python
from picomon import PicomonConfig, run_monitor

config = PicomonConfig(update_interval=1.5)
run_monitor(["--update-interval", str(config.update_interval)])
```

## Development

- Run tests with `pytest` (see the CI workflow for reference)
- Use `scripts/publish.py` to cut a GitHub release once tags are in place

## License

MIT © [Omar Kamali](https://omarkamali.com)

Source: <https://github.com/omarkamali/picomon>
