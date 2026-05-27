# P9 Release Readiness Boundary

## What P9 Is

P9 is release hygiene and install readiness. It turns the sealed local app into a usable personal release by adding documentation, verification, and onboarding.

## What P9 Is Not

- Not a new feature phase
- Not SaaS/cloud deployment
- Not multi-user support
- Not mobile app
- Not Windows/macOS packaging
- Not automatic P6 validation
- Not provider output persistence
- Not active YAML/rubric mutation

## Hard Boundaries

| Boundary | Enforcement |
|----------|-------------|
| No `alters/current/**` changes | git diff check |
| No `alters/calibration/rubric.yaml` changes | git diff check |
| No runtime records committed | git status check |
| No provider secrets committed | secret grep |
| No real provider calls | no live flags |
| No P6 validation claims | documentation review |
| No P6 seal | documentation review |
| No implementation after P9-000 | milestone gate |

## Success Standard

A fresh user/local machine can:
1. Install the .deb package
2. Launch the app via CLI
3. Configure mock provider
4. Run a smoke test
5. Backup data
6. Uninstall/upgrade safely
7. Understand P6/P8 boundaries

## Threat Model

| Threat | Impact | Mitigation |
|--------|--------|------------|
| Broken install | Cannot use app | Disposable install smoke |
| Broken upgrade | Data/config loss | Upgrade smoke with data check |
| Unsafe uninstall | Data/secrets leaked | Uninstall smoke, cleanup check |
| Unclear provider setup | User confusion | Provider setup guide |
| P6 misunderstanding | False confidence | Clear P6 state messaging |
| Docs/code divergence | Wrong instructions | Doc review against CLI |
| Secrets in logs | Credential leak | Backup smoke, secret grep |
