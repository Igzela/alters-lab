# Sample Data

This directory contains sample data for new users to explore Alters Lab immediately after installation.

## Scenario

The sample data models a relatable life transition: someone deciding between four mutually incompatible career paths:

- **Branch A** — Upskill in place while keeping current job, pursue internal transfer to data engineering
- **Branch B** — Relocate to a tech hub for a fresh start
- **Branch C** — Time-boxed dual-track experiment with evidence-based pivot
- **Branch D** — Build a public portfolio and let demonstrated capability open doors

## Loading Sample Data

```bash
alters-lab load-sample
```

This copies the sample data into `alters/current/` so the app has content on first boot.

## Files

| File | Description |
|------|-------------|
| `snapshot.yaml` | Current life state: constraints, uncertainties, anchors |
| `branches.yaml` | Four mutually incompatible career branches |
| `alters/alter_A-D.yaml` | One alter per branch with voice and personality |
| `reality_trace.yaml` | Empty reality trace (ready for calibration data) |

## Customization

After loading, edit the files in `alters/current/` to reflect your own situation. The app will use your data for dialogue, calibration, and weekly reviews.
