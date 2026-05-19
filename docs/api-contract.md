# API Contract

## v0.1 Status: DEFERRED

Phase 0 of Alters System is entirely file-based. No API layer is implemented or planned for v0.1.

## Future API (Reference Only)

When an API is eventually built, it will expose Alters System concepts:

### Snapshots

| Method | Path | Description |
|--------|------|-------------|
| POST | /snapshots | Capture current snapshot |
| GET | /snapshots/{id} | Get snapshot details |

### Branches

| Method | Path | Description |
|--------|------|-------------|
| GET | /snapshots/{id}/branches | List branches for snapshot |
| POST | /snapshots/{id}/branches | Create branch |
| GET | /branches/{id} | Get branch details |

### Alters

| Method | Path | Description |
|--------|------|-------------|
| GET | /branches/{id}/alters | List alters for branch |
| POST | /branches/{id}/alters | Generate alter |
| GET | /alters/{id} | Get alter details |

### Dialogue

| Method | Path | Description |
|--------|------|-------------|
| POST | /alters/{id}/dialogue | Start dialogue session |
| GET | /alters/{id}/dialogue | Get dialogue history |

### Calibration

| Method | Path | Description |
|--------|------|-------------|
| GET | /rubric | Get current rubric |
| POST | /rubric/score | Score branches |
| GET | /traces | Get reality traces |

## Notes

- All endpoints return Alters System entities only
- No content-project / script / publish / retro entities
- No external LLM provider calls
- Authentication: single-user, none required in v0.1
