# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-12-26

### Added
- **Multi-GPU Provider Support**: Now supports AMD, NVIDIA, and Apple Silicon GPUs through a pluggable provider architecture
- **New Textual-based TUI**: Complete rewrite using Textual framework for a modern, responsive terminal interface
- **Multiple Screens**:
  - Dashboard: Overview of all GPUs with live metrics and sparklines
  - System: CPU, RAM, and aggregate GPU cluster statistics
  - GPU Detail: Per-GPU detailed view with charts and history
  - Rig Card: Shareable ASCII art summary of your system
- **Rig Card Feature**: Generate and copy/save shareable system summaries (`c` to copy, `s` to save)
- **System Metrics**: CPU usage, RAM usage, load averages via psutil
- **Keyboard Navigation**: Full keyboard support with number keys (1-9) for quick screen switching
- **Help Screen**: Press `?` for keyboard shortcuts reference

### Changed
- Default UI is now Textual-based (use `--classic` flag for legacy curses UI)
- Providers auto-detect available GPU hardware on startup
- GPU indices now displayed consistently with HIP ID / device sorting

### Fixed
- Box-drawing alignment issues in exported rig cards
- Removed hardcoded "AMD" references - now shows actual GPU vendor/name

## [0.1.2] - 2025-12-12

### Changed
- Sort GPUs by HIP/node ID (mirroring the order seen by software honoring `CUDA_VISIBLE_DEVICES`, ROCm HIP runtime, etc.) so monitoring aligns with application-visible device indices.

## [0.1.1] - 2025-12-06

### Fixes
- Fix publishing workflow



## [0.1.0] - 2025-12-06

### Added
- `PicomonConfig` dataclass and argument parser options to control update frequency, history retention, and AMD SMI timeouts.
- Modular GPU polling helpers (`picomon.smi`) plus curses UI rendering (`picomon.ui`) with sparklines for GFX, power, and VRAM.

