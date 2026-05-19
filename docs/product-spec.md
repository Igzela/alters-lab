# Product Specification

## Cheat on Content - Calibration System for Content Creators

### 1. Overview

Cheat on Content is a calibration system that helps content creators improve content quality through structured prediction and retrospective analysis.

### 2. Core Loop

```
Score → Blind Prediction → Publish → T+3d Retro → Rubric Evolution
```

### 3. Domain Concepts

#### 3.1 Project

A content project represents a creator's ongoing content effort (e.g., "Tech Blog", "YouTube Channel").

#### 3.2 Rubric

A structured evaluation framework with criteria and weights. Rubrics evolve over time based on retrospective evidence.

#### 3.3 Script

A piece of content to be scored and predicted.

#### 3.4 Scoring

Evaluation of a script against the current rubric version.

#### 3.5 Blind Prediction

A prediction of content performance made before publishing. Immutable once created.

#### 3.6 Publish

Recording when content goes live and initial metrics.

#### 3.7 Retro

Post-publication review comparing predicted vs actual performance. Append-only.

#### 3.8 Calibration Signal

Insights derived from retro data, suggesting rubric adjustments. Requires human review.

### 4. User Stories

- As a creator, I want to score my content against a rubric so I understand its quality
- As a creator, I want to predict performance before publishing so I can track my judgment accuracy
- As a creator, I want to review actual performance vs prediction so I can calibrate my instincts
- As a creator, I want the rubric to evolve based on evidence so it stays relevant

### 5. Constraints (v0.1)

- Single user
- Local SQLite storage
- No real LLM integration
- No external API calls
