# oh-my-kimi (Python Edition) 🐍

<p align="center">
  <em>A high-performance, Python-native orchestrator for <strong>Kimi Code CLI</strong>.</em>
</p>

> [!TIP]
> **Which edition should I use?**
> - **🐍 Python Edition (Current)**: **Recommended.** Best for AI researchers, algorithm engineers, and Python-native workflows.
> - **📦 [NPM Edition](https://github.com/wang-h/oh-my-kimi)**: Best for full-stack developers and Node.js users.

---

## Overview
This is the official Python port of the `oh-my-kimi` orchestration framework. It provides **deep integration** with the Python-based `kimi-cli` ecosystem, enabling multi-agent collaboration, advanced skill management, and automated workflows without the overhead of cross-language bridging.

## Why Python Edition?
- **Native Integration**: Seamlessly share configurations, context, and environment variables with Kimi-CLI.
- **Python Skills**: Write custom agent skills in pure Python (`main.py`) instead of just Markdown.
- **Modern Performance**: Built with `Typer`, `Rich`, and `libtmux` for a fast, beautiful terminal experience.
- **No Node.js Required**: Pure Python environment, easy to install via `pip` or `uv`.

## Core Features
- [x] **Smart Pathing**: Unified resolution for `~/.kimi` and legacy `.codex` homes.
- [x] **Instruction Overlay**: Dynamic `AGENTS.md` injection with automated **Codebase Map** generation.
- [x] **Tmux Orchestration**: One-click multi-agent team setup (`omk team`).
- [x] **Real-time HUD**: High-refresh monitoring dashboard via `rich.live`.
- [x] **MCP Infrastructure**: Python-native Model Context Protocol servers for state and memory.

## Getting Started

### Prerequisites
- Python 3.10+
- `kimi-cli` (Python version)

### Installation
```bash
# Recommended: Install using uv for speed
uv pip install -e .

# Or using standard pip
pip install -e .
```

### Usage
```bash
# Check your environment
omk info

# Launch a multi-agent team
omk team "Refactor this module into cleaner abstractions"

# Single-turn ask with project context
omk ask "How does the plugin system work?"
```

## Comparison

| Feature | Python Edition (🐍) | NPM Edition (📦) |
| --- | --- | --- |
| **Language** | Python 3.10+ | TypeScript / Rust |
| **Integration** | Native (import/env) | Subprocess / Wrapper |
| **Skill Type** | Python (.py) & Markdown | Markdown (.md) |
| **Best For** | AI/Data Scientists | Full-stack Devs |
| **CLI Framework** | Typer / Rich | Yargs / Inquirer |

## Documentation
For more guides and a full skill catalog, visit the [Official Website](https://wang-h.github.io/oh-my-kimi-website/).

## License
MIT
