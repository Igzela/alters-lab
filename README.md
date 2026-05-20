# Alters System Lab

A personal future-branch simulation and calibration system.

## Overview

Alters System helps you explore potential future paths by modelling branching life decisions, generating alter versions of yourself for each path, and calibrating which branches best align with your values and energy.

## Core Loop

```
Intake → Branch Discovery → Alter Generation → Dialogue / Value Alignment → Calibration
```

1. **Intake** - Capture a current Snapshot: constraints, uncertainties, and what you refuse to give up
2. **Branch Discovery** - Identify structural, mutually incompatible future branches
3. **Alter Generation** - For each branch, generate an Alter: a coherent version of you living that path
4. **Dialogue / Value Alignment** - Converse with each Alter to evaluate fit, values, and tradeoffs
5. **Calibration** - Score branches against a Rubric and refine over time

## Phase 0: File-Based Workflow

Phase 0 operates entirely on local files — YAML snapshots, YAML branch definitions, YAML alters, and a JSON calibration state. No application code, no database, no LLM providers. This is the exploration and design phase before any system is built.

## Project Structure

```
alters/
  current/
    snapshot.yaml          # Current state: constraints, uncertainties, anchors
    branches.yaml          # Discovered branches with quality rules
    reality_trace.yaml     # How reality diverges from branches over time
    alters/                # Alter YAML files per branch
  calibration/
    rubric.yaml            # Evaluation dimensions (4-axis rubric)
    state.json             # Cold-start calibration state
    scores/                # Per-cycle score records
  archive/                 # Completed cycle archives
```

## Local Chrome CDP Proxy

`tools/cli.py` controls an existing GUI Chrome through CDP. To restart Chrome
with CDP on port `9222` and route browser traffic through the local Clash Verge
proxy at `http://127.0.0.1:7897`, run:

```bash
tools/start_chrome_proxy.sh
```

The script closes the matching Chrome instance for
`/tmp/chrome-debug-profile`, starts Chrome with `--proxy-server`, and keeps the
GUI display environment:

```bash
DISPLAY=:0
XAUTHORITY=/run/user/1000/.mutter-Xwaylandauth.DZGGP3
WAYLAND_DISPLAY=wayland-0
```

Verify access through CDP:

```bash
python3 tools/cli.py --timeout 60 navigate https://chatgpt.com/
python3 tools/cli.py --target-url chatgpt.com get-content
```

## License

TBD
