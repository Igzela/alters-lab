# Promotion Drafts

## Reddit Post

**Title:** I built an open-source tool to simulate different life paths and calibrate which ones actually align with your values

**Subreddits:** r/selfimprovement, r/decisions, r/opensource

**Body:**

I've been working on a personal project called **Alters Lab** — it's a local, open-source system that helps you explore structurally different life branches and figure out which ones actually work for you.

The core idea: your future isn't a single path. It's a branching tree. Alters Lab lets you:

- **Map your current situation** through a structured intake (constraints, directions, values)
- **Generate 3-4 life branches** — structurally different paths, not minor variations
- **Create "alter selves"** — hypothetical versions of you on each branch, with their own personality, skills trajectory, and voice
- **Dialogue with your alters** — ask them about their life, tradeoffs, regrets
- **Weekly calibration** — score how your real actions align with your stated intentions
- **Forecast & evaluate** — lock predictions, then check them against reality over time

What makes it different from journaling or life-planning apps:

1. **No single score** — it never tells you "your life is 7.2/10." It gives directional forecasts with explicit uncertainty.
2. **Route A + Route B** — combines your personal calibration data (Route A) with population-level evidence from longitudinal studies like NLSY97 and MIDUS (Route B)
3. **Calibration loop** — the system tracks whether your predictions actually came true, and adjusts
4. **Fully local** — YAML + JSON files, no cloud, no account. Your data stays on your machine.

Tech stack: React 18 + TypeScript + Tailwind frontend, Python/FastAPI backend, 1980 tests.

It's at v1.0, MIT licensed, runs via Docker or manual install. Looking for people who want to actually try it and give feedback.

**GitHub:** https://github.com/Igzela/alters-lab

Would love to hear thoughts — especially from anyone who's tried structured decision-making frameworks (like CFAR techniques, decision journals, etc.).

---

## Blog Post

# Why I Built a Life Simulation System (And Why Your Future Isn't a Single Path)

## The Problem

Most life-planning tools assume you're choosing between Option A and Option B. Pick one, commit, move on.

But life doesn't work like that. You're not choosing between "go to grad school" and "take the job." You're choosing between *entire versions of yourself* — with different skills, social circles, daily rhythms, and definitions of success.

I wanted a tool that could hold that complexity without reducing it to a spreadsheet.

## What Alters Lab Does

Alters Lab is a local, open-source system for simulating structurally different life branches. Here's the flow:

### 1. Snapshot Intake
You describe your current situation through three anchors:
- Your heaviest constraint
- What's most unclear
- What you're unwilling to give up

This isn't freeform journaling. It's structured to surface the real decision axes.

### 2. Branch Discovery
The system generates 3-4 life branches — not "should I take job A or job B" but structurally different life configurations. Each branch has:
- A core tradeoff
- Validation signals (what would tell you this is working)
- A 2-year trajectory sketch

### 3. Alter Generation
For each branch, you get an "alter" — a hypothetical future version of yourself who chose that path. Each alter has:
- Personality drift from your current self
- Skills trajectory
- Daily rhythm
- Voice profile (how they'd talk to you)

### 4. Dialogue
You can actually *talk* to your alters. Ask them about their life. What surprised them. What they'd do differently. This isn't fortune-telling — it's structured perspective-taking.

### 5. Weekly Calibration
Each week, you score how your real actions aligned with your stated intentions across three dimensions: direction, execution, and avoidance. Over time, the system detects patterns — like "you consistently over-commit on weeks after business trips."

### 6. Forecast & Evaluation
You lock predictions ("I think I'll complete the certification by March"), then the system tracks whether reality matched. It combines:
- **Route A**: Your personal calibration data (behavior trends, alignment scores)
- **Route B**: Population-level evidence from longitudinal studies (NLSY97, MIDUS)

The result is directional forecasts with explicit uncertainty bands, not false precision.

## Design Principles

**No life score.** The system never reduces your life to a single number. Life quality is multi-dimensional, and pretending otherwise is harmful.

**No exact probability.** "37% chance of career satisfaction" is theater. Alters Lab gives directional signals: improving, stable, declining, mixed.

**Calibration over prediction.** The goal isn't to predict the future correctly. It's to get better at knowing what you don't know — and to notice when your actions don't match your stated values.

**Local-first.** All data lives in YAML and JSON files on your machine. No cloud sync, no accounts, no telemetry. Your life story isn't a SaaS product.

## Who It's For

- People who've tried decision journals, CFAR techniques, or structured introspection and want a system to hold the complexity
- Anyone facing a major life decision (career change, relocation, relationship) who wants to think it through rigorously
- People who notice a gap between their stated values and actual behavior and want to close it

## Try It

```bash
git clone https://github.com/Igzela/alters-lab.git
cd alters-lab
docker compose up -d
# Open http://localhost:18790
```

MIT licensed. 1980 backend tests, 90 frontend tests. Runs entirely local.

**GitHub:** https://github.com/Igzela/alters-lab

---

## Quick Links for Posting

- Reddit r/selfimprovement: https://www.reddit.com/r/selfimprovement/submit
- Reddit r/decisions: https://www.reddit.com/r/decisions/submit
- Reddit r/opensource: https://www.reddit.com/r/opensource/submit
- Dev.to (for blog): https://dev.to/new
- Hashnode: https://hashnode.com
- Medium: https://medium.com
