---
name: "Bug report"
about: "Help us fix things by sharing repro details and diagnostics"
title: "[Bug] <describe the issue>"
labels: [bug]
assignees: []
---

## Summary

_One-liner describing the observed problem._

## Expected vs actual

- **Expected:**
- **Actual:**

## Environment

| Item | Version / value |
| --- | --- |
| picomon version (`picomon --version`) | |
| Python version (`python --version`) | |
| OS / Distro | |
| Terminal emulator | |

### GPU Provider (check one)

- [ ] AMD (via `amd-smi`)
- [ ] NVIDIA (via `nvidia-smi`)
- [ ] Apple Silicon

## Provider diagnostics

Please paste the output of `picomon --list-providers`:

```
<paste output here>
```

### For AMD GPUs

<details>
<summary>Click to expand AMD diagnostics</summary>

`amd-smi` version (`amd-smi --version`):
```
<paste version here>
```

Static info (`amd-smi static --vram --limit --json`):
```json
<paste output here>
```

Metrics (`amd-smi metric --usage --power --mem-usage --json`):
```json
<paste output here>
```

</details>

### For NVIDIA GPUs

<details>
<summary>Click to expand NVIDIA diagnostics</summary>

`nvidia-smi` version:
```
<paste nvidia-smi output here>
```

GPU info (`nvidia-smi --query-gpu=name,memory.total,power.limit --format=csv`):
```
<paste output here>
```

</details>

### For Apple Silicon

<details>
<summary>Click to expand Apple Silicon diagnostics</summary>

macOS version (`sw_vers`):
```
<paste output here>
```

System info (`system_profiler SPDisplaysDataType`):
```
<paste output here>
```

</details>

## Steps to reproduce

1. ...
2. ...
3. ...

## Additional context / screenshots

_Link logs, screenshots, or anything else that helps us diagnose._
