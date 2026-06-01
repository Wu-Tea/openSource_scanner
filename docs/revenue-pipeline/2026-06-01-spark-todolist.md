# Spark TODO List - Revenue Pipeline V1

## How To Use This File

Give Spark one task block at a time. Always include the Global Guardrails block with each task.

Do not ask Spark to read the full design unless a task explicitly says so. The long docs are reference material; this file is the small-context execution list.

Main success path:

`import-record -> extract pain -> match local tools -> judge -> select one bet -> plan experiment`

## Global Guardrails

Paste this above every Spark task:

```text
Repo: E:\AI\resp_scanner
OS: Windows. Use PowerShell commands only.

Hard rules:
- Do not create, restore, or enable recurring automation.
- Do not spawn subagents.
- Do not build live collectors yet.
- Do not touch untracked generated reports/records unless the task explicitly says manual smoke test.
- Keep existing CLI commands backward compatible.
- Keep default target solo-dev 2C/light consumer.
- Reject ERP/B2B/CRM/POS/accounting/inventory/procurement by default.
- Do not commit secrets, cookies, tokens, or account data.
- Prefer small modules and tests.

Reference docs only if needed:
- docs/revenue-pipeline/2026-06-01-spark-implementation-blueprint.md
- docs/revenue-pipeline/2026-06-01-design-review.md
```

## Task 0 - Orientation Only

Goal: understand current repo shape without editing.

Read only:

- `.agent-context/handoff.md`
- `src/open_source_scanner/__main__.py`
- `src/open_source_scanner/storage.py`
- `docs/revenue-pipeline/2026-06-01-spark-todolist.md`

Output:

- 5-bullet summary of what will be implemented.
- Confirm no automation/subagent/live collector work will be done.

Stop after summary. Do not edit files.

## Task 1 - Revenue Store Foundation

Goal: create durable revenue-pipeline tables and dataclasses.

Read only:

- `src/open_source_scanner/storage.py`
- `src/open_source_scanner/models.py`
- Blueprint Phase 1 in `docs/revenue-pipeline/2026-06-01-spark-implementation-blueprint.md`

Create:

- `src/open_source_scanner/revenue/__init__.py`
- `src/open_source_scanner/revenue/models.py`
- `src/open_source_scanner/revenue/store.py`
- `tests/revenue/test_revenue_store.py`

Implement:

- `EvidenceItem`
- `PainSignal`
- `ToolMatch`
- `OpportunityCandidate`
- `CandidateScore`
- `Bet`
- `Experiment`
- `RevenueStore.initialize()`
- basic upsert/list/get methods needed by later tasks

Done when:

- Empty temp SQLite initializes all tables.
- Evidence upsert is idempotent.
- `get_active_bet()` returns only active bet.
- Tests pass:

```powershell
uv run pytest tests/revenue/test_revenue_store.py -v
uv run ruff check src tests
```

Suggested commit:

```powershell
git add src/open_source_scanner/revenue tests/revenue/test_revenue_store.py
git commit -m "feat: add revenue pipeline store"
```

## Task 2 - Import Market-Pain Markdown

Goal: import existing Markdown records into revenue evidence without live scraping.

Read only:

- `records/market-pain/2026-06-01-1829.md` for manual shape inspection only
- `src/open_source_scanner/revenue/store.py`
- Blueprint Phase 2

Create:

- `src/open_source_scanner/revenue/import_record.py`
- `tests/revenue/test_import_record.py`
- small fixture under `tests/fixtures/revenue/`

Modify:

- `src/open_source_scanner/__main__.py`

Implement CLI:

```powershell
uv run oss-scan import-record records/market-pain/2026-06-01-1829.md
```

Rules:

- Tests must use fixture Markdown, not depend on untracked local records.
- Parser must tolerate mojibake/mixed language.
- Duplicate imports must not duplicate evidence.

Done when:

```powershell
uv run pytest tests/revenue/test_import_record.py -v
uv run pytest tests/test_cli.py tests/revenue/test_import_record.py -v
uv run ruff check src tests
```

Suggested commit:

```powershell
git add src/open_source_scanner tests/revenue tests/fixtures
git commit -m "feat: import market pain records"
```

## Task 3 - Pain Signal Extraction

Goal: convert imported evidence into consumer pain/desire categories.

Read only:

- `src/open_source_scanner/revenue/import_record.py`
- `src/open_source_scanner/revenue/store.py`
- Blueprint Phase 3

Create:

- `src/open_source_scanner/revenue/pain.py`
- `tests/revenue/test_pain.py`

Implement categories:

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

- ERP/B2B banned words must produce rejected categories.
- Do not use LLMs.
- Keep it deterministic and easy to test.

Done when:

```powershell
uv run pytest tests/revenue/test_pain.py -v
uv run ruff check src tests
```

Suggested commit:

```powershell
git add src/open_source_scanner/revenue/pain.py tests/revenue/test_pain.py
git commit -m "feat: extract consumer pain signals"
```

## Task 4 - Local Tool Matching

Goal: match pain signals to existing local GitHub opportunity rows.

Read only:

- `src/open_source_scanner/storage.py`
- `src/open_source_scanner/taxonomy.py`
- `src/open_source_scanner/revenue/pain.py`
- Blueprint Phase 4

Create:

- `src/open_source_scanner/revenue/tool_match.py`
- `tests/revenue/test_tool_match.py`

Implement:

- `match_local_opportunities(...)`
- `tool_match_score(...)`

Rules:

- Tool matches are accelerators, not demand proof.
- GPL/AGPL should create caution notes.
- B2B/ERP signals should not produce promoted matches.

Done when:

```powershell
uv run pytest tests/revenue/test_tool_match.py -v
uv run ruff check src tests
```

Suggested commit:

```powershell
git add src/open_source_scanner/revenue/tool_match.py tests/revenue/test_tool_match.py
git commit -m "feat: match tools for revenue signals"
```

## Task 5 - Candidate Judge

Goal: create product candidates and score them with hard gates.

Read only:

- `src/open_source_scanner/revenue/pain.py`
- `src/open_source_scanner/revenue/tool_match.py`
- Blueprint Phase 5
- Design Review P0/P1 findings

Create:

- `src/open_source_scanner/revenue/judge.py`
- `src/open_source_scanner/revenue/render.py`
- `tests/revenue/test_judge.py`

Modify:

- `src/open_source_scanner/__main__.py`

Implement CLI:

```powershell
uv run oss-scan judge --since-days 14 --output reports/revenue-pipeline/judgment.md
```

Must include:

- hard gate failures
- dimension scores
- optimist review
- skeptic review
- operator review
- platform/legal review

Done when:

```powershell
uv run pytest tests/revenue/test_judge.py -v
uv run pytest tests/test_cli.py tests/revenue/test_judge.py -v
uv run ruff check src tests
```

Suggested commit:

```powershell
git add src/open_source_scanner tests/revenue/test_judge.py
git commit -m "feat: judge revenue candidates"
```

## Task 6 - Bet Selector

Goal: select exactly one active revenue bet.

Read only:

- `src/open_source_scanner/revenue/judge.py`
- `src/open_source_scanner/revenue/store.py`
- Blueprint Phase 6
- Design Review P0 selector finding

Create:

- `src/open_source_scanner/revenue/bet_select.py`
- `tests/revenue/test_bet_select.py`

Modify:

- `src/open_source_scanner/__main__.py`

Implement CLI:

```powershell
uv run oss-scan select-bet --output-dir bets
```

Rules:

- Never create two active bets.
- If active bet exists, write/update backlog only.
- Rejected candidates cannot become active bets.
- `bets/current.md` must include thesis, audience, evidence, 14-day experiment, success criteria, kill criteria, next action.

Done when:

```powershell
uv run pytest tests/revenue/test_bet_select.py -v
uv run pytest tests/test_cli.py tests/revenue/test_bet_select.py -v
uv run ruff check src tests
```

Suggested commit:

```powershell
git add src/open_source_scanner tests/revenue/test_bet_select.py
git commit -m "feat: select active revenue bet"
```

## Task 7 - Experiment Planner

Goal: generate concrete experiment artifacts for the active bet.

Read only:

- `src/open_source_scanner/revenue/bet_select.py`
- `src/open_source_scanner/revenue/store.py`
- Blueprint Phase 7

Create:

- `src/open_source_scanner/revenue/experiment.py`
- `tests/revenue/test_experiment.py`

Modify:

- `src/open_source_scanner/__main__.py`

Implement CLI:

```powershell
uv run oss-scan plan-experiment --days 14 --output-dir experiments
```

Generate:

- `plan.md`
- `demo-scope.md`
- `landing-copy.md`
- `distribution-posts.md`
- `metrics.md`
- `review.md`

Rules:

- Fail clearly if no active bet exists.
- Every generated doc must include bet slug, target audience, hook, success criteria, kill criteria, and at least one distribution channel.

Done when:

```powershell
uv run pytest tests/revenue/test_experiment.py -v
uv run pytest tests/test_cli.py tests/revenue/test_experiment.py -v
uv run ruff check src tests
```

Suggested commit:

```powershell
git add src/open_source_scanner tests/revenue/test_experiment.py
git commit -m "feat: generate experiment artifacts"
```

## Task 8 - README And Final Smoke Test

Goal: document the new local pipeline and run full verification.

Read only:

- `README.md`
- Blueprint Phase 10

Modify:

- `README.md`

Add commands:

```powershell
uv run oss-scan import-record records/market-pain/2026-06-01-1829.md
uv run oss-scan judge --since-days 14
uv run oss-scan select-bet
uv run oss-scan plan-experiment --days 14
```

Must mention:

- recurring automation remains disabled
- ERP/B2B remains banned by default
- live collectors are not part of V1

Final verification:

```powershell
uv run pytest -v
uv run ruff check src tests
```

Manual smoke test:

```powershell
$env:OSS_SCANNER_DB="data/revenue-smoke.sqlite"
uv run oss-scan import-record records/market-pain/2026-06-01-1829.md
uv run oss-scan judge --since-days 30 --output reports/revenue-pipeline/smoke-judgment.md
uv run oss-scan select-bet --output-dir bets
uv run oss-scan plan-experiment --days 14 --output-dir experiments
Remove-Item Env:OSS_SCANNER_DB
```

Suggested commit:

```powershell
git add README.md
git commit -m "docs: document revenue pipeline commands"
```

## If Spark Runs Out Of Context

Tell it:

```text
Continue from docs/revenue-pipeline/2026-06-01-spark-todolist.md.
Do only the next unchecked task.
Read only the files listed in that task.
Do not implement live collectors or automation.
```

## First Task To Give Spark

Start with Task 1, not Task 0, if Spark already read this file and understands the guardrails.
