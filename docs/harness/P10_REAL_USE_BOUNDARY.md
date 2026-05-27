# P10 Real-Use Boundary

## What Counts as Real Use

Real use means Charlie uses Alters Lab as the primary weekly review tool, not as a test exercise. Real use produces real evidence that can feed P6 validation.

## Real Use Requirements

1. **Installed from .deb package** — not running from repo in dev mode
2. **Real weekly note** — Charlie writes a genuine weekly note in Obsidian, not a synthetic test note
3. **Real weekly review** — Charlie runs a real review session, not a walkthrough for documentation
4. **Real friction** — Charlie reports actual UX issues, not hypothetical ones
5. **Real time** — at least 4 weeks / 21 days of genuine use before P6 validation can start

## What Does NOT Count as Real Use

- Running from repo with `PYTHONPATH=... python -m alters_lab`
- Writing synthetic weekly notes for testing
- Running review sessions as documentation exercises
- Provider dry-run or mock mode exercises
- Any activity where the goal is to test the system, not to use it

## Evidence Boundary

| Artifact | Real Use | Synthetic/Test |
|----------|----------|----------------|
| Weekly note | Charlie's actual Obsidian note | Any note created for testing |
| Weekly review | Charlie's actual review session | Any review run for documentation |
| Calibration record | From real weekly review | From test/smoke runs |
| Action alignment | From real usage data | From synthetic data |
| Friction log | Issues discovered during real use | Hypothetical issues |

## P6 Validation Cannot Start Until

- Charlie has used the packaged app for real weekly reviews
- At least 4 real weekly review records exist
- At least 21 calendar days have passed
- Charlie explicitly authorizes P6 validation start
