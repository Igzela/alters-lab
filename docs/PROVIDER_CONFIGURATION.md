# Provider Configuration

Alters Lab connects to an LLM provider to power alter dialogue, weekly reviews, and other provider-backed features. This guide covers how to configure the provider.

## Provider Modes

Alters Lab supports three provider modes:

| Mode | Description |
|------|-------------|
| `disabled` | No LLM calls. Provider features return stub responses. Default out of the box. |
| `mock` | Simulated LLM responses. Useful for testing and development without an API key. |
| `openai-compatible-http` | Real LLM calls to any OpenAI-compatible HTTP API (OpenAI, MiMo API, local servers, etc.). |

## Configuration File

When installed as a `.deb` package, configuration lives at:

```
~/.config/alters-lab/config.yaml
```

In development mode, it lives at:

```
<repo>/alters/product/config/config.yaml
```

### Config Structure

```yaml
version: 1
mode: dev            # dev or packaged (set automatically)
server:
  host: 127.0.0.1
  port: 18790
  open_browser_on_start: true
paths:
  data_dir: /home/user/Projects/alters-lab
  state_dir: /home/user/Projects/alters-lab/alters/product/state
provider:
  mode: disabled                    # disabled | mock | openai-compatible-http
  openai_compatible_http:
    base_url: null                  # e.g. https://api.openai.com/v1
    model: null                     # e.g. gpt-4o, mimo-v2.5
    timeout_seconds: 60
  secrets:
    storage: keyring                # keyring | secrets_yaml_fallback
    key_name: alters-lab/provider-api-key
safety:
  active_yaml_write_allowed: false
  rubric_write_allowed: false
  provider_output_persists_by_default: false
  provider_output_can_write_active_yaml: false
```

## Setting Up openai-compatible-http Mode

### Step 1: Set provider mode

```bash
# Via API (while server is running)
curl -X POST http://127.0.0.1:18790/provider-config/config \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "openai-compatible-http",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4o",
    "timeout_seconds": 60,
    "secret_storage": "keyring",
    "key_name": "alters-lab/provider-api-key",
    "explicit_user_configuration": true
  }'
```

> **Important**: Setting `mode` to `openai-compatible-http` requires `explicit_user_configuration: true`. This is a safety gate to prevent accidental provider activation.

### Step 2: Store your API key

```bash
curl -X POST http://127.0.0.1:18790/provider-config/secret \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your-api-key-here",
    "storage": "keyring",
    "confirmation": "store-secret"
  }'
```

### Step 3: Verify configuration

```bash
# Check status
curl http://127.0.0.1:18790/provider-config/status

# Run a dry-run test
curl -X POST http://127.0.0.1:18790/provider-config/test \
  -H "Content-Type: application/json" \
  -d '{"dry_run": true}'
```

## Environment Variable Override

Provider settings can also be overridden via environment variables (highest priority):

| Variable | Description |
|----------|-------------|
| `ALTERS_PROVIDER_MODE` | Provider mode (`disabled`, `mock`, `openai-compatible-http`) |
| `ALTERS_PROVIDER_BASE_URL` | Base URL for the OpenAI-compatible API |
| `ALTERS_PROVIDER_API_KEY` | API key |
| `ALTERS_PROVIDER_MODEL` | Model name |

These take precedence over config.yaml values.

## Secret Storage

Alters Lab stores API keys securely using one of two backends:

### System Keyring (default)

If the `keyring` Python package is installed and available, API keys are stored in your system keyring (GNOME Keyring, KWallet, etc.). The key name is `alters-lab/provider-api-key`.

```bash
# Install keyring support (optional but recommended)
pip install keyring
```

### YAML Fallback

If keyring is unavailable, secrets are stored in:

```
~/.config/alters-lab/secrets.yaml
```

This file is created with `chmod 0600` (owner read/write only).

> **Warning**: The YAML fallback is less secure than system keyring. The file is readable by your user account. Do not commit it to version control.

### Deleting a Stored Key

```bash
curl -X DELETE http://127.0.0.1:18790/provider-config/secret \
  -H "Content-Type: application/json" \
  -d '{"confirmation": "delete-secret"}'
```

## API Endpoints

All provider configuration endpoints are under the `/provider-config` prefix.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/provider-config/health` | Health check for the config service |
| `GET` | `/provider-config/status` | Current provider status (redacted, no secrets) |
| `GET` | `/provider-config/config` | Current config (redacted, no API key value) |
| `POST` | `/provider-config/config` | Update provider config |
| `POST` | `/provider-config/secret` | Store an API key |
| `DELETE` | `/provider-config/secret` | Delete a stored API key |
| `POST` | `/provider-config/test` | Test provider configuration |

> **Security note**: API responses never return the actual API key value. The `api_key` field is always redacted or omitted.

## Safety Flags

Provider output is sandboxed regardless of mode:

- `provider_output_persists_by_default: false` — Provider responses are not saved by default.
- `provider_output_can_write_active_yaml: false` — Provider cannot modify `alters/current/` YAML files.
- `provider_output_can_generate_reality_score: false` — Provider cannot generate calibration scores.

These flags are enforced in the provider config and are not user-configurable.
