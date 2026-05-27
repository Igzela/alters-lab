# P10-M4 Real-Use Friction Log

## Summary

No blocker friction reported during first note ingest (P10-M2) and first weekly review session (P10-M3).

The core API workflow — ingest → start review → complete review → action alignment score — executed successfully via the packaged app at `http://127.0.0.1:18790`.

## Source Milestones

- **P10-M2**: First real weekly note ingested via packaged app API
- **P10-M3**: First real weekly review session completed via packaged app API (action alignment score: 0.75)

## Known Facts (Observed Only)

1. Packaged app started and served frontend at localhost:18790
2. `POST /obsidian-weekly-note/ingest` accepted structured weekly note and saved record
3. `POST /weekly-review/start` created review session from weekly note record
4. `POST /weekly-review/{session_id}/complete` recorded review details and next correction
5. `POST /action-alignment/score` scored alignment at 0.75 (aligned_progress)
6. Provider mode was mock; `provider_used=false` in all API responses
7. No live provider calls were made
8. No raw personal content was committed to the repository
9. P6 validation was not started (`p6_validation_started: false`, `p6_sealed: false`)

## Friction Items

### F-001: React textarea state sync in Weekly Review UI

```yaml
- id: F-001
  category: navigation/UI
  source_milestone: P10-M3
  severity: low
  observed: |
    Attempting to fill the Weekly Review textarea via browser automation
    (Chrome DevTools fill tool) did not trigger React state update. The
    "Ingest note" button remained disabled because React's controlled
    component state (rawNote) did not sync with the DOM value.
  impact: |
    Does not affect manual user interaction — users type directly into
    the textarea and React handles input events normally. Only affects
    browser automation / testing workflows.
  proposed_fix: |
    None needed for production use. If automation testing is desired,
    use direct API calls instead of UI automation.
  fix_scope: none
  validation_relevance: none
  status: accepted_no_fix
```

### F-002: Weekly note section validation strictness

```yaml
- id: F-002
  category: weekly note ingest
  source_milestone: P10-M3
  severity: low
  observed: |
    API ingest endpoint enforces required sections: Session Type,
    Observable Facts, Subjective State, Primary Problem,
    Friction / Avoidance, Desired Correction. A weekly note missing
    any section returns 422 with descriptive error.
  impact: |
    Positive behavior — prevents incomplete notes from entering the
    system. First-time users may need to restructure their note format
    to match required sections.
  proposed_fix: |
    None needed. Strict validation is intentional. Consider adding
    section hints in frontend UI if first-run friction is observed
    in future pilots.
  fix_scope: none
  validation_relevance: affects_pilot
  status: accepted_no_fix
```

### F-003: Provider mode mock — no real LLM guidance

```yaml
- id: F-003
  category: provider/mock boundary
  source_milestone: P10-M3
  severity: low
  observed: |
    Provider mode was mock throughout P10-M2 and P10-M3. Review
    session completed without LLM-generated suggestions. The assistant
    suggestion feature was not exercised.
  impact: |
    Expected behavior for pilot phase. Mock mode ensures no network
    calls and no secret exposure. Real provider enablement is a
    separate decision (P8 sealed, provider safety audit passed).
  proposed_fix: |
    None needed for P6 validation start. Real provider is optional
    and does not block review/scoring workflow.
  fix_scope: none
  validation_relevance: none
  status: accepted_no_fix
```

## Future Friction (Placeholder)

No additional friction items observed during P10-M2/P10-M3. Future friction should be logged here during ongoing weekly reviews in the pilot period.

## Conclusion

No blocker friction exists. The core workflow functions as designed. All observed friction items are low severity and accepted as-is or have no-fix-needed status.
