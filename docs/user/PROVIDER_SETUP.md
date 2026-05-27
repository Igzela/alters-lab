# Provider Setup Guide

Alters Lab supports three provider modes. The default is **disabled** — no LLM calls, no API key needed.

## Provider Modes

| Mode | Network | API Key | Use Case |
|------|---------|---------|----------|
| `disabled` | No | No | Safest default. Dialogue and review features work with structured prompts you can copy externally. |
| `mock` | No | No | Simulated responses for testing the UI and workflow without an API key or network. |
| `openai-compatible-http` | Yes | Yes | Real LLM-powered responses. Requires explicit setup. |

## Default: Disabled

Out of the box, the provider mode is **disabled**. You can use Weekly Review, paste notes, score action alignment, and explore the app without any LLM integration. Provider-dependent features (dialogue preview, weekly review assistant) will show structured prompts you can copy and use with any external LLM.

## Mock Mode

Switch to **mock** mode to test provider-dependent features without network calls or API keys:

1. Open the app at `http://127.0.0.1:18790`
2. Go to **Provider Settings**
3. Select `mock` from the Mode dropdown
4. Click **Save Config**

Mock mode returns simulated responses. No API key is needed. No network calls are made.

## Live Provider Setup (openai-compatible-http)

To enable real LLM-powered responses inside the app:

### 1. Configure the Provider

In **Provider Settings**:

- Set Mode to `openai-compatible-http`
- Enter your **Base URL** (e.g. `https://api.openai.com/v1` or any OpenAI-compatible endpoint)
- Enter your **Model** name (e.g. `gpt-4o`)
- Set **Timeout** (default 60 seconds)
- Choose **Secret storage**: `keyring` (recommended) or `secrets_yaml_fallback`
- Click **Save Config**

### 2. Store Your API Key

In the **API Key** section:

- Paste your API key into the Key field
- Click **Store Key**

The key is stored in your system keyring (preferred) or in `~/.config/alters-lab/secrets.yaml` with `chmod 0600`. The key is **never displayed again** after storage. The API never returns the key in responses.

To delete a stored key, click **Delete Key**.

### 3. Test the Connection

In the **Dry Run** section:

- Click **Test Provider Config**

This runs a dry-run connectivity check against the provider's `/models` endpoint. No prompts are sent. No provider output is generated. If it fails, check your base URL, API key, and network connectivity.

### 4. Use Provider Features

Once configured and tested:

- **Dialogue Preview**: Go to Dialogue, select an alter, and click Generate. Requires explicit confirmation before each network call. Output is labeled as unverified.
- **Weekly Review Assistant**: In Weekly Review Step 4, select a help type and click Generate Suggestion. Requires explicit confirmation. Output is advisory only — you must manually copy and edit.

## What P8 Means

P8 (sealed as REAL_PROVIDER_READY_LOCAL_APP) means the app has a safe provider integration boundary:

- Provider calls go through a single gateway
- API keys are never returned in responses
- Provider output is labeled unverified
- No automatic scoring or review completion
- Safety audit passed (7 sections)

P8 does **not** mean any specific provider account works. You still need to configure and test your own provider.

## Important Notes

- **No real API key examples** are shown in this documentation
- **Live provider calls are not run by default** — they require explicit user action
- **Connectivity check requires explicit confirmation** before making network calls
- **Dialogue preview requires explicit confirmation** before each generation
- **Weekly assistant live suggestion requires explicit confirmation** before each generation
- Provider output is always labeled as **unverified and advisory only**
