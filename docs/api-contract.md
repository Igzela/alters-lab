# API Contract - v0.1

## Base URL

`http://localhost:8000/api/v1`

## Endpoints

### Projects

| Method | Path | Description |
|--------|------|-------------|
| GET | /projects | List all projects |
| POST | /projects | Create a project |
| GET | /projects/{id} | Get project details |
| PUT | /projects/{id} | Update a project |
| DELETE | /projects/{id} | Delete a project |

### Rubrics

| Method | Path | Description |
|--------|------|-------------|
| GET | /projects/{id}/rubrics | List rubrics for project |
| POST | /projects/{id}/rubrics | Create a new rubric version |
| GET | /rubrics/{id} | Get rubric details |

### Scripts

| Method | Path | Description |
|--------|------|-------------|
| GET | /projects/{id}/scripts | List scripts for project |
| POST | /projects/{id}/scripts | Create a script |
| GET | /scripts/{id} | Get script details |
| PUT | /scripts/{id} | Update a script |

### Scoring

| Method | Path | Description |
|--------|------|-------------|
| POST | /scripts/{id}/score | Score a script against rubric |
| GET | /scripts/{id}/scores | Get scores for a script |

### Predictions

| Method | Path | Description |
|--------|------|-------------|
| POST | /scores/{id}/predict | Create blind prediction |
| GET | /scores/{id}/prediction | Get prediction (immutable) |

### Publishing

| Method | Path | Description |
|--------|------|-------------|
| POST | /scripts/{id}/publish | Record publication |
| GET | /scripts/{id}/publishes | Get publish history |

### Retrospectives

| Method | Path | Description |
|--------|------|-------------|
| POST | /predictions/{id}/retro | Record retro (append-only) |
| GET | /predictions/{id}/retros | Get retros for prediction |

### Calibration

| Method | Path | Description |
|--------|------|-------------|
| GET | /projects/{id}/signals | Get calibration signals |
| POST | /signals/{id}/review | Submit human review |

## Response Format

```json
{
  "data": {},
  "meta": {
    "timestamp": "ISO8601"
  }
}
```

## Error Format

```json
{
  "error": {
    "code": "string",
    "message": "string"
  }
}
```
