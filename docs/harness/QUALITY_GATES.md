# Quality Gates

## Non-Negotiable Gates

### Blind Prediction Immutability

Once a blind prediction is created, it CANNOT be modified. The prediction captures the creator's judgment at a specific moment in time.

### Rubric Bump Evidence

A rubric version bump requires evidence from at least 2 retrospectives showing consistent pattern. Single retros cannot drive rubric changes.

### Retro Append-Only

Retrospectives are append-only. Once recorded, they cannot be modified or deleted. This ensures an immutable audit trail of performance data.

### Calibration Signal Human Review

All calibration signals require human review before being acted upon. Automated signals are suggestions, not directives.

### No Real LLM Provider (v0.1)

v0.1 MUST NOT connect to any real LLM provider. All scoring and prediction uses deterministic algorithms or mock data.

## Quality Checklist

- [ ] All predictions are immutable after creation
- [ ] Rubric changes are backed by multi-retro evidence
- [ ] Retros are append-only
- [ ] Calibration signals require human review
- [ ] No external LLM API calls
