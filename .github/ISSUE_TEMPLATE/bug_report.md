---
name: "Bug report"
about: "Help us fix things by sharing repro details and diagnostics"
title: "[Bug] <describe the issue>"
labels: [bug]
assignees: []
---

## Summary

_One‑liner describing the observed problem._

## Expected vs actual

- **Expected:**
- **Actual:**

## Environment

| Item | Version / value |
| --- | --- |
| picomon version (`picomon --version`) | |
| Python version (`python --version`) | |
| OS / Distro | |
| `amd-smi` version (`amd-smi --version`) | |
| Terminal emulator | |

## Metrics command output

Please paste the raw JSON output of the commands picomon uses for metrics collection. Remove any sensitive info before posting.

```shell
amd-smi static --vram --limit --json
```

```
<paste static output here>
```

```shell
amd-smi metric --usage --power --mem-usage --json
```

```
<paste metric output here>
```

## Steps to reproduce

1. …
2. …
3. …

## Additional context / screenshots

_Link logs, screenshots, or anything else that helps us diagnose._
