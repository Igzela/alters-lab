# P10 Pilot Evidence Requirements

## Purpose

Define what evidence is collected during the P10 pilot, how it's stored, and what can/cannot be committed to the repo.

## Evidence Collected During Pilot

| Evidence Type | Collected | Stored Locally | Committed to Repo |
|---------------|-----------|----------------|-------------------|
| Weekly notes | Yes | Yes (Obsidian) | No |
| Weekly review records | Yes | Yes (app state) | Redacted summaries only |
| Calibration records | Yes | Yes (app state) | Redacted summaries only |
| Action alignment scores | Yes | Yes (app state) | Redacted summaries only |
| Friction log | Yes | Yes (local file) | Yes (anonymized) |
| Provider prompts/responses | Yes (if provider enabled) | Yes (local) | No |
| Runtime artifacts | Yes | Yes (local) | No |
| Secrets/API keys | Yes (if provider enabled) | Yes (keyring) | No |

## Committing Evidence to Repo

The repo may store:

- **Redacted summaries** — anonymized, no personal content
- **Friction logs** — anonymized UX issues
- **Phase status** — what phase we're in, not what data we have
- **Decision records** — what decisions were made, not what data triggered them

The repo must NOT store:

- Raw weekly notes
- Raw weekly review content
- Provider prompts or responses
- Personal data
- Secrets or API keys
- Runtime artifacts with personal content

## Evidence Summary Format

When committing evidence summaries, each must state:

```yaml
evidence_type: weekly_review_summary
source: real_use
time_period: 2026-W21 to 2026-W24
record_count: 4
personal_content: redacted
synthetic: false
```

The `synthetic` field must be `false` for any evidence that will feed P6 validation. If `synthetic: true`, the evidence cannot count toward P6 validation requirements.

## Friction Log Format

```yaml
friction_id: F001
discovered_date: 2026-05-27
area: provider_settings
severity: minor
description: "Dry-run button label unclear"
fix_status: deferred
fix_scope: docs_only
```

Friction logs may be committed to the repo. They must not contain personal content.
