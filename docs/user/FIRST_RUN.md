# First Run

After installing Alters Lab, this guide walks you through launching the app and understanding what it does.

For a step-by-step checklist, see [First-Run Checklist](FIRST_RUN_CHECKLIST.md).

## Start the App

```bash
alters-lab start
```

This starts the local server and opens your browser to `http://127.0.0.1:18790`.

If the browser doesn't open automatically:

```bash
alters-lab open
```

## What is Alters Lab?

Alters Lab is a personal future path simulation and calibration system. It helps you:

1. **Capture your current state** (Snapshot) — constraints, uncertainties, and what you won't give up
2. **Discover structural branches** — 3-4 mutually incompatible future paths
3. **Generate Alters** — coherent versions of yourself living each path
4. **Dialogue with Alters** — evaluate fit, values, and tradeoffs
5. **Calibrate** — score branches against a rubric and refine over time

It is **not** a content creation tool, productivity app, or decision-making bot. It simulates and calibrates — you decide.

## Provider Mode

The default provider mode is **disabled**. Dialogue and weekly review features work without a provider — they use structured prompts that you can copy and use with any LLM externally.

You can switch to **mock provider** mode in the Provider Settings page (`http://127.0.0.1:18790` → Provider Settings). Mock mode returns simulated responses with no API key and no network calls.

To enable real LLM-powered responses inside the app, see [Provider Setup](PROVIDER_SETUP.md).

Live provider features (dialogue preview, weekly review assistant) require explicit confirmation before making network calls. Provider output is always labeled as unverified and never auto-submits reviews or scores. See [Provider Safety](PROVIDER_SAFETY.md) for details.

## Try a Smoke Test

```bash
alters-lab doctor
```

This runs health checks on the local installation: layout, config, data directories, port availability, frontend, and provider mode.

## What is P6 / P7 / P8?

The project progressed through numbered phases:

- **P6** — Personal long-term use hardening (code complete, not behavior-validated, not sealed)
- **P7** — Local app distribution (sealed as LOCAL_APP_RELEASE_CANDIDATE)
- **P8** — Real provider integration (sealed as REAL_PROVIDER_READY_LOCAL_APP)

P6 behavior validation requires 4 weeks of real use. It has not started. Do not assume P6 is validated.

## Weekly Review

The primary way to use Alters Lab is through **Weekly Review**:

1. Open the app at `http://127.0.0.1:18790`
2. Navigate to **Weekly Review**
3. Paste your weekly note (from Obsidian or any text source)
4. Review the extracted records
5. Start the review session
6. Score your action alignment
7. Complete the review

Each weekly review creates calibration records that track your patterns over time.

Provider suggestions (if enabled) are advisory only — you remain responsible for all review content and scores.

## Stopping the App

```bash
alters-lab stop
```

Your data persists across restarts. No data is lost when you stop the server.

## Troubleshooting

If something doesn't work, see [Troubleshooting](TROUBLESHOOTING.md) or run `alters-lab doctor`.
