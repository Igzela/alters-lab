# Data Model

## Entities

### Project

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| name | str | Project name |
| description | str | Optional description |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |

### Rubric

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| project_id | UUID | FK to Project |
| version | int | Version number |
| criteria | JSON | List of criteria with weights |
| created_at | datetime | Creation timestamp |

### Script

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| project_id | UUID | FK to Project |
| title | str | Script title |
| content | text | Script content |
| created_at | datetime | Creation timestamp |

### Scoring

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| script_id | UUID | FK to Script |
| rubric_id | UUID | FK to Rubric |
| scores | JSON | Per-criterion scores |
| total_score | float | Weighted total |
| created_at | datetime | Creation timestamp |

### BlindPrediction

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| scoring_id | UUID | FK to Scoring |
| predicted_metrics | JSON | Predicted performance metrics |
| confidence | float | Confidence level (0-1) |
| created_at | datetime | Creation timestamp |

### Publish

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| script_id | UUID | FK to Script |
| published_at | datetime | Publication timestamp |
| platform | str | Publishing platform |
| initial_metrics | JSON | Metrics at time of publish |

### Retro

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| prediction_id | UUID | FK to BlindPrediction |
| actual_metrics | JSON | Actual performance metrics |
| delta_analysis | JSON | Predicted vs actual analysis |
| notes | text | Creator notes |
| created_at | datetime | Creation timestamp |

### CalibrationSignal

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| project_id | UUID | FK to Project |
| signal_type | str | Type of signal |
| evidence | JSON | Supporting evidence |
| suggested_rubric_change | JSON | Proposed rubric modification |
| human_reviewed | bool | Whether human has reviewed |
| human_verdict | str | Human's decision |
| created_at | datetime | Creation timestamp |

## Relationships

- Project 1:N Rubric
- Project 1:N Script
- Script 1:N Scoring
- Scoring 1:1 BlindPrediction
- Script 1:N Publish
- BlindPrediction 1:N Retro
- Project 1:N CalibrationSignal
