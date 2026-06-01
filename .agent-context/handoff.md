# Handoff

## Current Objective

Build `openSource_scanner` into a local-first Revenue Pipeline for solo-developer-friendly 2C and lightweight consumer opportunities.

The goal is not to produce more research documents by default. The system should turn public pain signals and repository/tool signals into one active revenue bet, with a clear experiment plan and execution path.

## Product Model

Think of the project as an opportunity engine:

`public pain signals -> opportunity judge -> bet selector -> experiment plan -> execution artifacts -> revenue review`

Existing GitHub scanning, community scanning, reports, memos, and market-pain records are input sources. They are not the final output.

## Hard Defaults

- Default target: solo-developer-friendly 2C/light consumer opportunities.
- Preferred categories: entertainment, games, desktop companions, browser toys, creator toys, learning/focus/social/hobby micro-products, and playful utilities with small-hit potential.
- Default non-goal: heavy B2B workflow products.
- ERP and adjacent enterprise operations software are banned from default scans and recommendations.
- Old B2B, workflow-family, vertical-business, and ERP-adjacent scan results are historical data only. Do not use them as the mainline unless the user explicitly reopens that direction.
- `market-pain-radar` automation was deleted by the user. Do not recreate it until the Revenue Pipeline includes judgment and execution layers.
- This workspace is Windows/PowerShell. Use Windows-compatible commands and libraries by default.
- Do not store or commit secrets, cookies, tokens, private account data, or unnecessary personal data.
- Do not auto-commit generated `records/` or `reports/` artifacts unless the user asks.

## Current State

- Repository `https://github.com/Wu-Tea/openSource_scanner.git` is cloned at `E:\AI\resp_scanner`.
- The original GitHub-only MVP exists: config, GitHub connector, normalizer, scoring, SQLite storage, Markdown reports, Typer CLI, README, and workflow docs.
- Safety controls exist for GitHub scanning: per-run request budget, request spacing, rate-limit state capture, rate-limit floor stop, and fail-closed safety config validation.
- Existing report modes and configs include broad GitHub category scans, vertical-focus scans, and consumer scan presets.
- Strategic direction changed on 2026-05-20 from heavy B2B/vertical workflows to solo-developer 2C/light consumer products.
- ERP was banned from default scans on 2026-05-20.
- A one-off market-pain radar smoke run on 2026-06-01 wrote `records/market-pain/2026-06-01-1829.md` and updated `records/market-pain/index.md`; these are generated local artifacts.
- No active Codex automation should be assumed. The previous `market-pain-radar` automation was intentionally removed.

## Next Action

Implement the Revenue Pipeline before recreating any recurring automation:

1. `opportunity-judge`: read recent market-pain records and scan results, cluster pain signals, match useful repositories/tools, apply skeptic review, and score solo-dev revenue fit.
2. `bet-selector`: choose one active bet instead of leaving a pile of candidates; write something like `bets/current.md`.
3. `experiment-planner`: turn the selected bet into a 7-day or 14-day validation/execution plan with concrete build, distribution, and pricing tests.
4. `revenue-reviewer`: periodically evaluate evidence and decide continue, kill, or pivot.
5. Only after those pieces exist, recreate a recurring automation that produces judgment and action outputs, not just Markdown research notes.

## Blockers

- None known.

## Active Questions

- None requiring user input. The user authorized autonomous planning and development, with worktree/subagent delegation when useful.

## Relevant Decisions

- `.agent-context/decisions/DEC-2026-05-15-001-v1-github-local-mvp.md`
- `.agent-context/decisions/DEC-2026-05-16-001-balanced-category-reports.md`
- `.agent-context/decisions/DEC-2026-05-20-001-solo-dev-2c-mainline.md`
- `.agent-context/decisions/DEC-2026-05-20-002-ban-erp-from-default-scans.md`
- `.agent-context/decisions/DEC-2026-06-01-001-revenue-pipeline-mainline.md`

## Files To Read First

- `.agent-context/decisions/DEC-2026-06-01-001-revenue-pipeline-mainline.md`
- `.agent-context/decisions/DEC-2026-05-20-001-solo-dev-2c-mainline.md`
- `.agent-context/decisions/DEC-2026-05-20-002-ban-erp-from-default-scans.md`
- `docs/research/2026-05-20-solo-dev-2c-entertainment-pivot.md`
- `docs/research/2026-05-20-fragmented-waiting-time-games.md`
- `docs/automation/market-pain-radar.md`
- `.agent-context/session-log.md`

## Historical Context

- `docs/superpowers/plans/2026-05-15-open-source-opportunity-scanner.md` records the original GitHub scanner build plan.
- `docs/research/2026-05-19-deep-research-direction.md` records the earlier service-led workflow/B2B direction. Treat it as superseded for default work.
- `.agent-context/archive/session-log-2026-05-15-pre-compaction.md` is only needed for deeper pre-compaction history.

## Notes

- If future sessions feel pulled toward B2B, ERP, or generic open-source ranking, re-read `Current Objective`, `Hard Defaults`, and `DEC-2026-06-01-001-revenue-pipeline-mainline.md`.
- If repository state diverges, update this handoff after implementation rather than appending more historical detail here.
