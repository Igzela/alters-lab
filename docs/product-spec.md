# Product Specification

## Alters Lab -- Personal Future-Branch Simulation and Calibration System

### 1. Overview

Alters Lab is a personal tool for exploring potential future life paths. It captures a snapshot of your current life state, discovers structural branching decisions, generates coherent alter versions of yourself for each branch, and calibrates which paths best align with your values and energy through ongoing weekly review cycles.

The system runs locally on your machine as a web application served at `http://127.0.0.1:18790`. All data is stored as YAML and JSON files in the `alters/` directory. No database is required.

### 2. Core Loop

```
Snapshot --> Branch Discovery --> Alter Generation --> Dialogue --> Calibration
```

1. **Snapshot** -- A structured capture of your current life state: heaviest constraint, most unclear direction, and what you are unwilling to give up. Serves as the anchor for all branch generation.
2. **Branch Discovery** -- Identification of 3-4 structurally distinct, mutually incompatible future branches. Branches differ in kind, not degree.
3. **Alter Generation** -- For each branch, an Alter is generated: a coherent version of you living that path, with consistent values, tradeoffs, and narrative.
4. **Dialogue** -- You converse with each Alter to evaluate fit, values, and tradeoffs. Replies are not persisted unless explicitly saved.
5. **Calibration** -- Branches are scored against a rubric and refined over time through weekly review cycles. Calibration accumulates evidence across weeks to track behavioral patterns and alignment trends.

### 3. Features by Page

#### 3.1 System Status

Displays the current state of the application:

- Runtime mode, config path, and product data directory
- Whether the frontend is available
- Provider mode (disabled, mock, or openai-compatible-http)
- Storage backend (YAML + JSON)
- Whether any secrets are exposed in the status output (should always be "no")
- List of safe public endpoints

Provides a direct action button to start a Weekly Review.

#### 3.2 Getting Started

An onboarding checklist with four steps:

1. **Check system health** -- Verify the app is running correctly via the Status page.
2. **Configure provider** -- The app starts in disabled mode (no LLM calls). Switch to mock mode to test dialogue features without an API key, or configure a live provider.
3. **Run your first Weekly Review** -- Paste a weekly note, review extracted records, and score your action alignment.
4. **Back up your data** -- Run the backup command to snapshot your data.

Steps are tracked in the browser (localStorage) and can be marked complete or incomplete. Each step includes a navigation button to the relevant page.

#### 3.3 Weekly Review

A six-step guided flow for weekly self-reflection and calibration:

1. **Paste Weekly Note** -- Enter a freeform weekly note or use the built-in template. The note is ingested and structured into typed fields.
2. **Review Extracted Record** -- Inspect the structured output: session type (personal, project, learning, relationship), observable facts, subjective state, primary problem, friction or avoidance point, and desired correction. All fields are editable. A correction note is required to save edits.
3. **Start Review Session** -- Select an Alter to associate with the review (or leave blank for system recommendation). A review session is created.
4. **Complete Review** -- Write a review note, dialogue summary, primary next correction, and up to two supporting actions. An optional assistant panel can generate suggestions (dry-run or live, depending on provider mode). Suggestions are advisory only and must be manually copied into the review fields.
5. **Action Alignment Score** -- Rate three dimensions on a 0-1 scale: direction alignment, execution consistency, and avoidance level. Provide action evidence, avoidance evidence, and next correction evidence. Select a verdict label (aligned progress, noisy progress, avoidance disguised as work, recovery week, unstable but useful, or blocked by environment) and write a verdict sentence.
6. **Completion Summary** -- Displays the saved note record ID, review session ID, score record ID, and alignment score.

#### 3.4 Alter Dialogue

A chat interface for conversing with individual Alters:

- Select an Alter from the dropdown (Alter A through Alter D, or dynamically loaded from the current data).
- Type a message and send it.
- Receive a reply from the selected Alter.
- Replies are not persisted unless explicitly saved. Provider output is not treated as fact.

#### 3.5 Reality Score

Manual score submission for calibrating branches against reality:

- Select an Alter/branch pair.
- Rate four dimensions on a 1-5 scale: execution discipline, exploration freedom, life state match, and energy level.
- Add notes.
- Submit the score. Scores are marked as explicit user submissions.
- Recent action alignment scores from weekly reviews are displayed for reference.
- This page is separate from the weekly review flow. For structured weekly calibration, use Weekly Review instead.

#### 3.6 Calibration History

A read-only view of all calibration data accumulated over time:

- **Weekly Reviews** -- List of all review sessions with status, associated note record, creation date, and next correction.
- **Action Alignment** -- All alignment scores sorted by date, with a trend indicator (improving, declining, stable, or first score). Each score is expandable to show detailed dimensions (direction alignment, execution consistency, avoidance level), evidence (action, avoidance, next correction), verdict label with description, and the user's own verdict sentence.
- **Calibration Records** -- Raw score data from reality score submissions.
- **Drift Evidence** -- Records where actual outcomes diverged significantly from predicted branches.

#### 3.7 Rubric Delta

Generates suggestions for how the evaluation rubric might be adjusted based on accumulated calibration data. Suggestions are in pending_review status and cannot be applied automatically. The user must review and manually incorporate any changes.

#### 3.8 Checkpoint Plan

Generates a plan based on accumulated calibration data. Plans are in pending_review status and cannot be regenerated automatically. The user must review and manually act on any generated plan.

#### 3.9 Provider Settings

Configure the LLM provider that powers dialogue and weekly review suggestions:

- **Status card** -- Shows current mode, whether configured, base URL status, model status, API key storage status, secret storage method, whether secrets are redacted, whether provider output persists by default, whether the provider can write active YAML, and whether it can generate reality scores.
- **Configuration form** -- Set mode (disabled, mock, openai-compatible-http), base URL, model name, timeout (1-600 seconds), and secret storage method (keyring or secrets_yaml_fallback).
- **API key management** -- Store or delete an API key. Keys are never displayed after storage.
- **Dry run test** -- Test the provider configuration without making a live network call (unless in openai-compatible-http mode, in which case a network call is made but clearly indicated).

Safety notes are prominently displayed: default mode is disabled, mock mode requires no API key, live mode requires explicit configuration and confirmation before each network call, and provider output is unverified and advisory only.

#### 3.10 Pattern Review

Detects repeated behavioral patterns across multiple weekly reviews:

- Build a new pattern review by evaluating accumulated weekly review data.
- Each review shows the number of weeks evaluated and which patterns were triggered.
- Triggered patterns include: Noisy Progress, Avoidance Disguised as Work, Sleep Breakdown, Over Scope, Action Mismatch, and Correction Failure.
- Each triggered pattern shows occurrences, confidence level, and a strategy constraint.
- Pattern review is supporting evidence only. Provider output is not counted as evidence.

#### 3.11 Behavior Validation

Evaluates whether your behavior has actually improved based on accumulated evidence:

- Aggregates weekly reviews, calibration records, and pattern reviews.
- Reports an outcome: behavior validated, failed to validate, usage invalid, or insufficient data.
- **Metrics** -- Whether action alignment scores improve, whether repeated negative patterns reduce, and whether primary correction completion rate improves.
- **Usage Integrity** -- Whether weekly notes were completed honestly, calibration records were created, primary corrections were set, failure reviews were honest, self-deception risk was not softened, and sessions were not skipped too often.
- Requires accumulated evidence (minimum 4 weekly reviews, 4 calibration records, spanning 21+ days).

#### 3.12 Data Management

View, export, and delete product data:

- **Record counts** -- Shows the number of records in each data area.
- **Export** -- Export all data or individual areas. All exports redact secrets. Exported data is saved to a file on disk.
- **Delete by Record ID** -- Delete a specific record by entering its area, record ID, and typing "delete" to confirm. This is a destructive operation.
- **Archive** -- Currently disabled. Requires exact record selection.
- Long-term save is enabled by default.

### 4. Provider Modes

| Mode | Description |
|------|-------------|
| `disabled` | No LLM calls. Default out of the box. No API key needed. |
| `mock` | Simulated responses. No network calls, no API key. Useful for testing dialogue features. |
| `openai-compatible-http` | Real LLM calls to any OpenAI-compatible API. Requires explicit configuration and API key storage. |

### 5. CLI Commands

| Command | Description |
|---------|-------------|
| `alters-lab start` | Start the local server (opens browser automatically) |
| `alters-lab stop` | Stop the local server |
| `alters-lab status` | Show server status |
| `alters-lab doctor` | Run health checks |
| `alters-lab open` | Open the app in a browser (starts server if not running) |
| `alters-lab backup` | Create a data backup |
| `alters-lab load-sample` | Load sample data for new users |

### 6. Data Safety

- **No secrets exposed** -- API keys and secrets are never displayed in status output or API responses. All secrets are redacted.
- **Approval tokens for writes** -- Destructive operations (delete, live provider calls, secret storage) require explicit confirmation tokens typed by the user.
- **Local-only by default** -- The application runs on `127.0.0.1:18790`. No external network calls are made unless the user explicitly configures a live provider.
- **Provider output is advisory** -- LLM-generated content is never treated as authoritative. Users must manually review and copy any provider output that becomes part of their data.
- **No auto-inference from dialogue** -- Reality scores require explicit user submission. The system does not infer scores from conversation content.

### 7. Sample Data

Alters Lab ships with a sample data set that can be loaded via `alters-lab load-sample`. The sample includes a career-change scenario with:

- 1 snapshot
- 4 branches
- 4 alters (one per branch)

This data is loaded into `alters/current/` and provides a working example for exploring dialogue, calibration, and weekly reviews immediately after installation. The files in `alters/current/` can be edited to reflect your own situation.

### 8. Storage Structure

```
alters/
  current/          Active snapshot, branches, and alters
  sample/           Sample data for new users
  calibration/      Rubric, scores, and calibration state
  archive/          Completed cycle archives
```

All data is stored as YAML and JSON files. No database is required.

### 9. Non-Goals

- No multi-user support
- No cloud sync or remote storage
- No content creation or publishing features
- No real-time collaboration
- No mobile native app
