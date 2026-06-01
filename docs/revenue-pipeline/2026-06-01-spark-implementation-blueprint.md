# Spark Implementation Blueprint - Revenue Pipeline

## Overview

This blueprint is for implementing the Revenue Pipeline with a fast coding model such as 5.3 Spark.

The product goal is simple: turn public market signals into one selected revenue bet and one experiment plan. The implementation should extend the current Typer + SQLite + Markdown architecture instead of replacing it.

Do not implement recurring automation in this pass.

## Current Code Map

Existing files to preserve:

- `src/open_source_scanner/__main__.py`: Typer CLI commands.
- `src/open_source_scanner/storage.py`: SQLite store for GitHub opportunities.
- `src/open_source_scanner/models.py`: dataclasses and type aliases.
- `src/open_source_scanner/scoring.py`: current repository scoring.
- `src/open_source_scanner/report.py`: Markdown opportunity reports.
- `src/open_source_scanner/connectors/github.py`: GitHub REST connector.
- `tests/`: pytest coverage.

New implementation should add focused modules rather than making existing files huge.

## Target File Structure

Create:

```text
src/open_source_scanner/revenue/
  __init__.py
  models.py
  store.py
  import_record.py
  evidence.py
  pain.py
  tool_match.py
  judge.py
  bet_select.py
  experiment.py
  render.py
  profiles.py

tests/revenue/
  test_revenue_store.py
  test_import_record.py
  test_pain.py
  test_judge.py
  test_bet_select.py
  test_experiment.py

config/revenue/
  consumer-2c.yml
```

Modify:

```text
src/open_source_scanner/__main__.py
README.md
```

Optional later:

```text
src/open_source_scanner/connectors/hn.py
src/open_source_scanner/connectors/v2ex.py
src/open_source_scanner/connectors/itch.py
```

V1 can ship without live non-GitHub collectors by importing existing Markdown records and using current GitHub rows as tool accelerators.

## Phase 1: Data Model And Store

Goal: create durable tables for revenue-pipeline data without disturbing the existing `opportunities` table.

Implement in `src/open_source_scanner/revenue/models.py`:

- `EvidenceItem`
- `PainSignal`
- `ToolMatch`
- `OpportunityCandidate`
- `CandidateScore`
- `Bet`
- `Experiment`

Implement in `src/open_source_scanner/revenue/store.py`:

- `RevenueStore.initialize()`
- `RevenueStore.upsert_evidence(item)`
- `RevenueStore.list_evidence(since_days=None)`
- `RevenueStore.upsert_pain_signal(signal)`
- `RevenueStore.link_signal_evidence(signal_id, evidence_id, relevance, note)`
- `RevenueStore.upsert_tool_match(match)`
- `RevenueStore.upsert_candidate(candidate)`
- `RevenueStore.save_candidate_score(score)`
- `RevenueStore.get_active_bet()`
- `RevenueStore.create_bet(candidate_id, slug, success_criteria, kill_criteria)`
- `RevenueStore.update_bet_status(bet_id, status)`
- `RevenueStore.create_experiment(...)`

Testing requirements:

- Tables initialize on an empty temporary SQLite file.
- Upserts are idempotent.
- `get_active_bet()` returns only `status = active`.
- Unique source URL/source ID constraints prevent duplicates.

Implementation notes:

- Reuse `sqlite3` like existing `OpportunityStore`.
- Store list/dict fields as JSON text.
- Keep migrations simple in V1: `CREATE TABLE IF NOT EXISTS`.

## Phase 2: Import Existing Market-Pain Records

Goal: turn current Markdown records into structured evidence.

Implement in `src/open_source_scanner/revenue/import_record.py`:

- Parse title/date from `# Market Pain Record - ...`.
- Parse `## Sources Touched` URLs as source-run evidence.
- Parse `## Pain Signals` headings and bullets.
- Parse `## Tool / Repo Matches` as optional tool match seeds.
- Parse `## Opportunity Hypotheses` as candidate seeds.

Expected behavior:

- The parser is tolerant of mojibake or mixed-language text.
- It stores source URL and summary, not full page content.
- It can import `records/market-pain/2026-06-01-1829.md`.
- It returns an import summary: evidence count, pain headings, tool matches, candidate seeds.

CLI:

```powershell
uv run oss-scan import-record records/market-pain/2026-06-01-1829.md
```

Test cases:

- A tiny synthetic Markdown record imports three evidence items.
- Duplicate import does not duplicate evidence.
- Missing sections do not crash; they produce warnings in the summary.

## Phase 3: Pain Signal Extraction

Goal: normalize evidence into pain/desire clusters.

Implement in `src/open_source_scanner/revenue/pain.py`:

- `extract_pain_signals(evidence_items, profile) -> list[PainSignal]`
- `cluster_key_for_text(text, profile) -> str`
- `infer_consumer_category(text, profile) -> str`

V1 categories:

- `desktop_companion`
- `microgame`
- `creator_toy`
- `learning_focus`
- `social_hobby`
- `job_resume`
- `unknown_consumer`
- `rejected_b2b`
- `rejected_erp`

Rules:

- ERP/B2B words trigger rejected categories unless explicitly overridden.
- Evidence from the same heading/source theme can cluster together.
- Each signal should retain linked evidence IDs.

Test cases:

- Desktop pet/codex/focus text becomes `desktop_companion`.
- Meme/avatar/generator text becomes `creator_toy`.
- Idle/incremental/browser game text becomes `microgame`.
- ERP/CRM/POS/accounting/inventory text is rejected.

## Phase 4: Tool Matching

Goal: connect pain signals to existing GitHub opportunities or newly searched repositories.

V1 should start with local DB matching before new network calls.

Implement in `src/open_source_scanner/revenue/tool_match.py`:

- `match_local_opportunities(pain_signal, opportunity_rows) -> list[ToolMatch]`
- `tool_match_score(pain_signal, opportunity_row) -> int`

Data source:

- Existing `OpportunityStore.list_ranked(limit=...)`.
- Use title, description, topics, packaging signals, license, stars, recency.

Rules:

- Tool matches are accelerators, not proof.
- Libraries can be accepted as implementation references but should not become product bets by themselves.
- GPL/AGPL should produce license caution notes.

Test cases:

- `desktop_companion` matches desktop pet repos.
- `creator_toy` matches meme/avatar generator repos.
- B2B/ERP signals produce no promoted matches.

## Phase 5: Candidate Builder And Judge

Goal: build product-shaped candidates and score them with hard gates.

Implement in `src/open_source_scanner/revenue/judge.py`:

- `build_candidates(pain_signals, tool_matches, profile) -> list[OpportunityCandidate]`
- `judge_candidate(candidate, evidence, tool_matches, profile) -> CandidateScore`
- `render_judgment_report(candidates, scores) -> str`

Hard gates:

- `banned_erp_or_b2b`
- `no_consumer_audience`
- `no_distribution_path`
- `not_14_day_demo`
- `unauthorized_ip_dependency`
- `generic_ai_wrapper`
- `requires_live_ops_or_multiplayer`

Default score dimensions:

- pain/desire evidence: 0-20
- emotional pull/shareability: 0-15
- 10-second hook: 0-15
- solo buildability: 0-20
- distribution fit: 0-15
- monetization clarity: 0-15
- tool acceleration: 0-10
- freshness: 0-10
- competition wedge: 0-10
- risk penalty: 0 to -40

Candidate templates:

- Desktop companion/focus loop:
  - audience: AI-heavy workers, developers, students, focus-tool users.
  - distribution: V2EX, Product Hunt, itch.io, Steam demo later.
  - monetization: paid app/game, supporter/cosmetic pack.
- Creator toy:
  - audience: meme makers, creators, fandom/community operators.
  - distribution: social share cards, Product Hunt, Xiaohongshu/Bilibili, Chrome extension if applicable.
  - monetization: template packs, watermark-free export, paid pack.
- Microgame:
  - audience: idle/browser/cozy game players.
  - distribution: itch.io first, Steam demo later.
  - monetization: paid download, supporter DLC, Steam release.
- Learning/focus:
  - audience: learners, AI-assisted students, developers practicing skills.
  - distribution: HN/V2EX/Reddit/Product Hunt.
  - monetization: paid app, packs, subscription only if retention exists.

CLI:

```powershell
uv run oss-scan judge --since-days 14 --output reports/revenue-pipeline/judgment.md
```

Test cases:

- A strong desktop companion signal produces a scored candidate.
- A generic AI wrapper fails hard gate.
- A B2B workflow candidate is rejected.
- Judgment report includes optimist, skeptic, operator, and platform review.

## Phase 6: Bet Selector

Goal: select exactly one active revenue bet.

Implement in `src/open_source_scanner/revenue/bet_select.py`:

- `select_bet(candidates, scores, existing_active_bet) -> BetSelectionResult`
- `render_current_bet(...) -> str`
- `render_backlog(...) -> str`

Rules:

- If an active bet exists, do not replace it automatically.
- If no candidate passes hard gates, write a no-bet report with why.
- If multiple candidates pass, choose highest confidence-adjusted score.
- Always write success and kill criteria.

Default success criteria examples:

- 20 qualified visits from one target channel.
- 5 users click/demo/download/wishlist/signup.
- 2 users ask for access, price, release date, platform support, or paid version.
- For games/companions: at least 3 users say they would keep it open/use it during work or study.

Default kill criteria examples:

- No one understands the hook after one screenshot/GIF.
- No distribution channel responds.
- Prototype scope keeps expanding beyond 14 days.
- Legal/IP risk cannot be reduced.

CLI:

```powershell
uv run oss-scan select-bet --output-dir bets
```

Test cases:

- No active bet creates `bets/current.md`.
- Existing active bet only updates backlog.
- Rejected candidates never become active bets.

## Phase 7: Experiment Planner

Goal: generate concrete artifacts for the selected bet.

Implement in `src/open_source_scanner/revenue/experiment.py`:

- `plan_experiment(active_bet, days=14) -> ExperimentPlan`
- `write_experiment_artifacts(plan, output_dir)`

Artifact files:

- `plan.md`
- `demo-scope.md`
- `landing-copy.md`
- `distribution-posts.md`
- `metrics.md`
- `review.md`

Each artifact should be useful without reading code:

- `plan.md`: calendar, assumptions, success/kill criteria.
- `demo-scope.md`: what to build and what to explicitly exclude.
- `landing-copy.md`: title, tagline, bullets, CTA, FAQ, pricing test.
- `distribution-posts.md`: posts for V2EX/HN/Product Hunt/Reddit/itch/Steam depending on bet type.
- `metrics.md`: manual metrics table.
- `review.md`: continue/kill/pivot template.

CLI:

```powershell
uv run oss-scan plan-experiment --days 14 --output-dir experiments
```

Test cases:

- Planner creates all expected files.
- Planner refuses when no active bet exists.
- Markdown includes success and kill criteria.

## Phase 8: Revenue Review

Goal: make a decision after the experiment.

Implement in `src/open_source_scanner/revenue/review.py` or `experiment.py`:

- `parse_metrics(path)`
- `review_experiment(experiment, metrics) -> ReviewDecision`
- `write_review(decision)`

Decision values:

- `continue`
- `kill`
- `pivot`
- `defer`

CLI:

```powershell
uv run oss-scan review-bet --metrics experiments/2026-06-01-example/metrics.md
```

Test cases:

- Strong metrics produce `continue`.
- Empty/weak metrics produce `kill` unless review notes justify `defer`.
- Review updates bet status.

## Phase 9: CLI Integration

Modify `src/open_source_scanner/__main__.py`.

Add commands:

- `import-record`
- `judge`
- `select-bet`
- `plan-experiment`
- `review-bet`

Do not remove existing commands.

Use a helper:

```text
_revenue_store() -> RevenueStore
```

It should use the same `OSS_SCANNER_DB` environment variable as `OpportunityStore`.

## Phase 10: Documentation

Update `README.md` with:

- One paragraph explaining Revenue Pipeline.
- PowerShell command examples.
- Note that recurring automation is still disabled.
- Note that ERP/B2B remains banned by default.

Add output examples:

```powershell
uv run oss-scan import-record records/market-pain/2026-06-01-1829.md
uv run oss-scan judge --since-days 14
uv run oss-scan select-bet
uv run oss-scan plan-experiment --days 14
```

## Testing Commands

Use Windows-compatible commands:

```powershell
uv run pytest -v
uv run ruff check src tests
```

Focused runs:

```powershell
uv run pytest tests/revenue -v
uv run pytest tests/test_cli.py tests/revenue -v
```

## Spark Coding Rules

- Do not create or enable automations.
- Do not spawn subagents.
- Do not touch untracked generated reports unless explicitly asked.
- Keep existing CLI commands backward compatible.
- Prefer small modules with deterministic behavior.
- Add tests before implementation when practical.
- Use no new dependencies unless absolutely necessary.
- Use PowerShell examples only.
- Never commit secrets or user account data.

## Implementation Order

Recommended commit sequence:

1. `feat: add revenue pipeline store`
2. `feat: import market pain records`
3. `feat: extract consumer pain signals`
4. `feat: match tools for revenue signals`
5. `feat: judge revenue candidates`
6. `feat: select active revenue bet`
7. `feat: generate experiment artifacts`
8. `feat: review revenue experiments`
9. `docs: document revenue pipeline commands`

Each commit should leave tests passing.

## Self-Review Checklist For Spark

Before finishing implementation:

- Does `oss-scan import-record` work on `records/market-pain/2026-06-01-1829.md`?
- Does `oss-scan judge` create a judgment report?
- Does `oss-scan select-bet` create exactly one `bets/current.md` when no active bet exists?
- Does the selector avoid replacing an existing active bet?
- Does `oss-scan plan-experiment` create all six experiment files?
- Does ERP/B2B filtering still reject banned categories?
- Do tests pass on Windows with PowerShell commands?
- Did implementation avoid recreating scheduled automation?
