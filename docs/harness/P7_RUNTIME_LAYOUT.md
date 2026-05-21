# P7 Runtime Layout

## Exact Paths

Application code:

- `/opt/alters-lab`

Executable launcher:

- `/usr/bin/alters-lab`

Desktop file:

- `/usr/share/applications/alters-lab.desktop`

User config:

- `~/.config/alters-lab/config.yaml`

User secrets:

- Preferred: system keyring.
- Fallback: `~/.config/alters-lab/secrets.yaml` with mode `0600`.

User data root:

- `~/.local/share/alters-lab`

Runtime records:

- `~/.local/share/alters-lab/product/weekly_notes/`
- `~/.local/share/alters-lab/product/weekly_reviews/`
- `~/.local/share/alters-lab/product/calibration_records/`
- `~/.local/share/alters-lab/product/pattern_reviews/`
- `~/.local/share/alters-lab/product/behavior_validation/`
- `~/.local/share/alters-lab/product/exports/`

Logs:

- `~/.local/state/alters-lab/logs/`

Protected repository paths:

- `alters/current/**`
- `alters/calibration/rubric.yaml`

## Config Schema Draft

```yaml
version: 1
mode: packaged
server:
  host: 127.0.0.1
  port: 18790
  open_browser_on_start: true
paths:
  app_root: /opt/alters-lab
  config_dir: ~/.config/alters-lab
  data_dir: ~/.local/share/alters-lab
  state_dir: ~/.local/state/alters-lab
provider:
  mode: disabled
  openai_compatible_http:
    base_url: null
    model: null
    timeout_seconds: 60
  secrets:
    storage: keyring
    key_name: alters-lab/provider-api-key
safety:
  active_yaml_write_allowed: false
  rubric_write_allowed: false
  provider_output_persists_by_default: false
  provider_output_can_write_active_yaml: false
```

Supported provider modes:

- `disabled`
- `mock`
- `openai-compatible-http`

Secret storage values:

- `keyring`
- `secrets_yaml_fallback`

When `secrets_yaml_fallback` is used, `~/.config/alters-lab/secrets.yaml` must be created with mode `0600` and must never be committed.

## Data Migration Notes

P6 repo-mode runtime records currently live under repo runtime areas such as product weekly notes, weekly reviews, calibration records, pattern reviews, behavior validation, and exports.

P7 must not automatically migrate or fabricate P6 evidence. Migration is a user-controlled copy/import operation.

Migration rules:

- Dev mode may continue using existing repo-compatible paths.
- Packaged mode starts with user-owned directories under `~/.local/share/alters-lab`.
- Any import from repo runtime directories must copy records into the user data directory, not move them.
- Raw runtime records must not be committed.
- Migration must not modify `alters/current/**`.
- Migration must not modify `alters/calibration/rubric.yaml`.
- Migration must preserve record timestamps and source metadata when present.
- Behavior validation state must remain blocked unless real persisted evidence satisfies the P6 validation gate.

## Dev/Prod Detection Strategy

Runtime mode should be resolved in a single app runtime config resolver.

P7-M1 implementation:

- Resolver module: `apps/api/src/alters_lab/services/runtime_layout.py`
- P6 runtime integration: `apps/api/src/alters_lab/services/p6_runtime.py`
- API status routes: `/runtime-layout/health`, `/runtime-layout/status`, `/runtime-layout/ensure-config`
- Dev mode remains repo-compatible.
- Packaged mode writes P6 runtime records under `~/.local/share/alters-lab/product/`.
- `/runtime-layout/status` returns redacted layout status and does not create config files.
- `/runtime-layout/ensure-config` creates `config.yaml` only; it does not create secrets or runtime records.

Detection precedence:

1. Explicit CLI flag, for example `--mode dev` or `--mode packaged`.
2. Environment variable, for example `ALTERS_LAB_MODE`.
3. Installed app marker, for example application root under `/opt/alters-lab`.
4. Fallback to dev mode when running from a repo checkout.

Dev mode:

- May use repo paths.
- Must keep tests compatible with `tmp_path`.
- Must keep active YAML/rubric write protections.

Packaged mode:

- Must use user data, config, state, and log directories.
- Must not require a repo checkout.
- Must bind local server to `127.0.0.1` by default.
- Must protect active YAML/rubric even if a repo path is present.
