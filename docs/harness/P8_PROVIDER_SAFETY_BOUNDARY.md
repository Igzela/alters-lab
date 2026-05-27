# P8 Provider Safety Boundary

## Provider Modes

| Mode | Description | Network | Persistence |
|------|-------------|---------|-------------|
| disabled | No provider configured. All provider features hidden. | None | None |
| mock | Deterministic mock responses for testing. | None | None |
| openai-compatible-http | Real provider via OpenAI-compatible HTTP API. | Yes | User-initiated only |

## Safety Rules

### Secret Handling

1. `config.yaml` stores non-secret provider config only: provider mode, base_url, model, timeout, secret storage mode, key name. API keys must never be stored in `config.yaml`.
2. Preferred secret storage is system keyring when available.
3. Fallback secret storage is `~/.config/alters-lab/secrets.yaml` with `chmod 0600`.
4. API responses never return API keys. Status/config endpoints show `***`.
5. Logs never include API keys. Logs contain audit metadata only (provider name, status code, latency).
6. Frontend never stores keys in localStorage. Password inputs do not store keys in React state beyond the input lifecycle.
7. Backup excludes secrets by default. Inclusion requires exact confirmation.

### Provider Output Handling

1. Provider output is displayed as preview only by default.
2. No provider output persists without explicit user confirmation.
3. No provider output writes to `alters/current/**`.
4. No provider output writes to `alters/calibration/rubric.yaml`.
5. No provider output creates reality scores or action alignment scores.
6. No provider output creates behavior validation records.

### Network Behavior

1. All provider interactions are user-initiated. No background or scheduled calls.
2. Connectivity check is dry-run by default. Live check requires explicit user action.
3. Network attempts are audited with redacted metadata (provider name, status code, latency).
4. Timeout is explicit. No automatic retry loops.
5. Failed requests are logged as audit events, not retried.

### UI Behavior

1. Provider output is labeled "unverified" in the UI.
2. Provider suggestions cannot auto-submit forms.
3. User must manually edit/confirm any provider-suggested content.
4. Action alignment scores remain user-submitted. No automatic scoring.

## Audit Events

Provider audit events record:
- Timestamp
- Provider mode (mock / openai-compatible-http)
- Endpoint called
- Status code (or error type)
- Latency
- Whether output was persisted (true/false)

Audit events do NOT record:
- API keys
- Raw prompt content
- Raw provider response content
- User personal records
