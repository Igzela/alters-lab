# First-Run Checklist

After installing Alters Lab, follow this checklist to get started.

## 1. Verify Installation

```bash
alters-lab doctor
```

This checks layout, config, data directories, port availability, frontend, and provider mode. All checks should pass.

## 2. Start the App

```bash
alters-lab start
```

Opens your browser to `http://127.0.0.1:18790`. If the browser does not open:

```bash
alters-lab open
```

## 3. Confirm Provider Mode

The app starts with provider mode **disabled** by default. No LLM calls are made. No API key is needed.

You can verify this on the **Provider Settings** page or by running:

```bash
alters-lab status
```

If you want to test the dialogue and review assistant features without network calls, switch to **mock** mode in Provider Settings. Mock mode returns simulated responses — no API key, no network.

Do not enter real API keys unless you are intentionally configuring a provider. See [Provider Configuration](../PROVIDER_CONFIGURATION.md) for details.

## 4. Import a Weekly Note

1. Open the app at `http://127.0.0.1:18790`
2. Go to **Weekly Review**
3. Paste your weekly note from Obsidian, a text file, or any source
4. Review the extracted records (constraints, uncertainties, anchors, branches)

## 5. Start a Weekly Review

1. After importing a note, click **Start Review**
2. Review the generated alter dialogue prompts
3. Score your action alignment (execution discipline, exploration freedom, life state match, energy level)
4. Complete the review

Each review creates calibration records that track your patterns over time.

## 6. Back Up Your Data

Before uninstalling or making risky changes:

```bash
alters-lab backup
```

This creates a `.tar.gz` in the `exports/` directory containing your product data and config. See [Data and Backup](DATA_AND_BACKUP.md) for options.

## 7. Understand the Boundaries

**P6 is not behavior-validated and not sealed.** P6 code is complete, but the 4-week real-use validation has not started. Do not assume P6 is validated.

**Provider suggestions are unverified and advisory only.** If you enable a provider, its output is labeled as unverified. You remain responsible for all review content and scores. Provider suggestions never auto-submit.

**Project phases:**

| Phase | Status |
|-------|--------|
| P6 | Code complete, not behavior-validated, not sealed |
| P7 | Sealed as LOCAL_APP_RELEASE_CANDIDATE |
| P8 | Sealed as REAL_PROVIDER_READY_LOCAL_APP |

## What to Do Next

- Run your first Weekly Review
- Explore the History page to see calibration records accumulate
- Optionally configure a provider for LLM-powered dialogue (see [Provider Configuration](../PROVIDER_CONFIGURATION.md))
- Check `alters-lab status` anytime to see current state
