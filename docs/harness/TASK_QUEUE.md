# Task Queue

## Execution Slices

### COC-001: Repo skeleton + governance docs

**Status**: running
**Goal**: Initialize repository structure and governance documentation
**Allowed files**: README.md, AGENTS.md, docs/**
**Forbidden**: apps/**, packages/**, .env, pyproject.toml, package.json, any business code

### COC-002: Backend schema definitions (Pydantic models)

**Status**: todo
**Goal**: Define Pydantic v2 models for all domain entities
**Depends on**: COC-001

### COC-003: SQLite data layer

**Status**: todo
**Goal**: Implement SQLite database layer with migrations
**Depends on**: COC-002

### COC-004: Rubric & scoring service

**Status**: todo
**Goal**: Build rubric management and content scoring service
**Depends on**: COC-003

### COC-005: Blind prediction service

**Status**: todo
**Goal**: Implement blind prediction creation and storage
**Depends on**: COC-004

### COC-006: Publish + Retro service

**Status**: todo
**Goal**: Build publish tracking and retrospective workflow
**Depends on**: COC-005

### COC-007: Calibration signal service

**Status**: todo
**Goal**: Implement calibration signal generation with human review
**Depends on**: COC-006

### COC-008: Minimal frontend

**Status**: todo
**Goal**: Build minimal Next.js frontend for core workflow
**Depends on**: COC-007
