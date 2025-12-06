# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-12-06

### Added
- First public release of **picomon** packaged as a `src/` layout library with a `picomon` CLI.
- `PicomonConfig` dataclass and argument parser options to control update frequency, history retention, and AMD SMI timeouts.
- Modular GPU polling helpers (`picomon.smi`) plus curses UI rendering (`picomon.ui`) with sparklines for GFX, power, and VRAM.
- GitHub Actions for CI testing and trusted PyPI publishing.
- Basic test suite that verifies configuration validation and AMD SMI parsing without requiring an actual AMD GPU.

