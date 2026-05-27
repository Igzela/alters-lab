# Troubleshooting

Common issues and how to fix them.

## Diagnostics

Run `alters-lab doctor` to check your installation:

```bash
alters-lab doctor
alters-lab doctor --json
```

This checks runtime layout, config, data directories, port, frontend, provider mode, secrets, and safety flags. Each check reports PASS, WARN, or FAIL with a recommended fix.

## App Will Not Start

1. Run `alters-lab doctor` — check for BLOCKED items
2. Check if the port is already in use (see below)
3. Check logs: `~/.local/state/alters-lab/logs/`
4. Try stopping first: `alters-lab stop`
5. Try starting again: `alters-lab start`

## Browser Does Not Open

```bash
alters-lab open
```

If this does not work, open `http://127.0.0.1:18790` manually in your browser.

## Port 18790 Already in Use

Another process is using the port. Options:

1. Stop the other process
2. Stop Alters Lab if it's running: `alters-lab stop`
3. Check what's on the port: `ss -tlnp | grep 18790`

## Package Installed but Command Missing

If `alters-lab` is not found after installing the `.deb`:

1. Check installation: `dpkg -l | grep alters-lab`
2. Check PATH: `which alters-lab`
3. The launcher is at `/usr/bin/alters-lab`
4. Reinstall if needed: `sudo apt install ./alters-lab_0.1.0_amd64.deb`

## Frontend Missing or 503

If the app starts but the UI shows a placeholder or 503:

1. Run `alters-lab doctor` — check the `frontend_dist` item
2. If building from source: `cd apps/web && npm run build`
3. If using a package: reinstall the `.deb`

## Provider Issues

### Disabled Mode (Default)

No LLM calls are made. Dialogue and review features show structured prompts you can copy externally. This is the safest mode.

### Mock Mode

Returns simulated responses. No API key needed. No network calls. Good for testing the UI.

### Live Mode (openai-compatible-http)

Requires explicit setup. See [Provider Setup](PROVIDER_SETUP.md).

- **Dry-run test fails**: Check that mode, base URL, and model are configured. The dry-run does not make network calls — it only checks local config.
- **Live connectivity check fails**: Check your API key, base URL, and network. The connectivity check may call the provider's `/models` endpoint.
- **No provider output**: Ensure you click Generate and confirm the network call.

## Keyring Unavailable

If keyring is not available on your system:

1. The app falls back to `secrets.yaml` with `chmod 0600`
2. You can change secret storage in Provider Settings
3. Check doctor output for `secrets_file` status

## Fallback secrets.yaml Permissions

If doctor reports secrets file permissions are not 0600:

```bash
chmod 600 ~/.config/alters-lab/secrets.yaml
```

## Backup Fails

1. Check that the data directory exists and is writable
2. Try dry-run first: `alters-lab backup --dry-run --json`
3. Check logs for errors

## Uninstall Did Not Delete User Data

This is by design. `sudo apt remove alters-lab` removes the package files but preserves your data:

- Config: `~/.config/alters-lab/`
- Data: `~/.local/share/alters-lab/`
- Logs: `~/.local/state/alters-lab/`

To fully remove everything, see [Uninstall](UNINSTALL.md).

## P6 Still Not Validated / Sealed

P6 (Personal Long-Term Use Hardening) is code complete but not behavior-validated and not sealed. The 4-week real-use validation has not started. This is expected — do not assume P6 is validated.

## Where Logs Are

Application logs are at:

```
~/.local/state/alters-lab/logs/
```

## Useful Commands

| Command | Purpose |
|---------|---------|
| `alters-lab doctor` | Check installation health |
| `alters-lab doctor --json` | Doctor output as JSON |
| `alters-lab status` | Check if the server is running |
| `alters-lab stop` | Stop the server |
| `alters-lab backup --dry-run --json` | Preview what backup would include |
| `alters-lab start` | Start the server |
