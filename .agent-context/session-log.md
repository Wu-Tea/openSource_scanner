# Session Log

This file is the primary session-history entry point. Detailed pre-compaction history for 2026-05-15 is preserved at `.agent-context/archive/session-log-2026-05-15-pre-compaction.md`.

## Milestones

### 2026-05-15 - Repository sync and MVP foundation

- Cloned `https://github.com/Wu-Tea/openSource_scanner.git` into `E:\AI\resp_scanner`.
- Created the implementation plan at `docs/superpowers/plans/2026-05-15-open-source-opportunity-scanner.md`.
- Initialized `.agent-context/` and accepted the V1 decision: local-first Python CLI, GitHub-only source, rule scoring, SQLite history, Markdown reports.

### 2026-05-15 - GitHub-only scanner MVP

- Implemented config, GitHub connector, normalization, scoring, SQLite storage, Markdown reports, Typer CLI, README docs, and Chinese workflow docs.
- Subagents implemented independent worktree slices and reviewers required fixes for HTTP error clarity, limit validation, duplicate scoring, malformed report JSON, feedback-not-found behavior, feedback targets, and network-error UX.
- Verified with `uv run pytest -v`, `uv run ruff check src tests`, CLI help, empty report generation, and missing-feedback behavior.

### 2026-05-15 - Scheduled automation

- Added `.github/workflows/daily-scan.yml` for daily/manual GitHub Actions scans.
- Added `scripts/run-daily-scan.ps1` for Windows Task Scheduler.
- Verified tests, ruff, and PowerShell parser.

### 2026-05-15 - Real scan/report verification

- Ran a small real GitHub scan with a temporary SQLite DB.
- Generated and inspected a temporary report containing feedback targets, scoring explanations, license data, and penalties.
- Removed temporary DB/report artifacts.

### 2026-05-15 - Opportunity memo workflow

- Added `oss-scan memo SOURCE SOURCE_ID`.
- Added Chinese memo rendering, safe filenames, overwrite protection, and `--force`.
- Reviewers required Chinese structural text and overwrite protection; both were fixed.
- Verified tests, ruff, memo help, and a temporary real scan/report/memo flow.

## Recent Active Checkpoints

### 2026-05-15 - Shortlist pipeline report

**Goal:** Turn `saved`, `watch`, and `package` feedback into a lightweight opportunity pipeline view.

**What changed:**

- Added `OpportunityStore.list_by_feedback(statuses, limit)`.
- Added `src/open_source_scanner/shortlist.py`.
- Added `oss-scan shortlist --statuses package,watch,saved --limit 50 --output reports/shortlist.md`.
- Updated README with shortlist workflow usage.

**Subagent results:**

- Worker H / Zeno implemented shortlist storage query, renderer, CLI, README docs, and tests.
- Kierkegaard's spec review approved the implementation.
- Godel's quality review required deterministic tie-breakers and empty-status rejection.
- Zeno fixed both issues.
- Euler re-reviewed the fixes and approved them.

**Verification:**

- `uv run pytest -v` -> 44 passed.
- `uv run ruff check src tests` -> all checks passed.
- `uv run oss-scan --help` showed `shortlist`.
- A temporary real scan/report/feedback/shortlist flow succeeded: one candidate was marked `package`, appeared under the Package group, and temporary files were removed.

**Context files updated:**

- `.agent-context/handoff.md`
- `.agent-context/session-log.md`
- `.agent-context/archive/session-log-2026-05-15-pre-compaction.md`

**Follow-up:**

- Push latest `main` to origin.
- Next likely feature: improve opportunity quality by adding configurable source queries and perhaps issue/discussion signals, or add a richer experiment status layer if the shortlist report proves useful.

### 2026-05-15 - GitHub safety controls and larger scan

**Goal:** Add safety guardrails before pulling more GitHub results, then run a larger scan.

**What changed:**

- Added safety config under `config/sources.yml`.
- Increased `github.max_results` to 100.
- Added fail-closed safety validation for request budget, request spacing, rate-limit floor, and boolean parsing.
- Added GitHub rate-limit state parsing from response headers.
- Added scan safeguards: request budget, request spacing, early stop when remaining quota reaches the configured floor, and CLI overrides.
- Updated README safety guidance.

**Subagent results:**

- Worker I / Hilbert implemented the safety controls with TDD.
- Bacon's spec review approved the implementation.
- Archimedes's quality review required fail-closed safety config validation.
- Hilbert fixed validation and added regression tests.
- Helmholtz re-reviewed and approved the fix.

**Verification:**

- Worker reported RED tests first, then `uv run pytest -v` -> 52 passed and `uv run ruff check src tests` -> all checks passed.
- Coordinator reran `uv run pytest -q` -> 52 passed.
- Coordinator reran `uv run ruff check src tests` -> all checks passed.
- Coordinator verified `uv run oss-scan scan --help` shows safety override options.
- Larger real scan: `uv run oss-scan scan --limit 100 --max-search-requests 10` -> 500 observations from 5 GitHub search requests.
- Generated `reports/2026-05-15.md` with Top 100 opportunities.
- SQLite now contains 472 unique opportunities; all are currently `new`.

**Context files updated:**

- `.agent-context/handoff.md`
- `.agent-context/session-log.md`

**Follow-up:**

- Review the generated report and mark the best candidates as `package`, `watch`, or `saved`.
- Consider adding issue/discussion/release-detail enrichment only for top-ranked or feedback-marked candidates.

### 2026-05-16 - Diversified category reporting

**Goal:** Respond to user feedback that the scan results were almost entirely AI-related.

**What changed:**

- Replaced the AI-heavy GitHub query set with a broader portfolio across developer tools, self-hosted infrastructure, automation, DevOps, security, monitoring, data engineering, analytics, CLI, and a capped AI query.
- Added `src/open_source_scanner/taxonomy.py` for lightweight category classification without changing the SQLite schema.
- Changed `oss-scan report` to default to balanced category output, with `--global` for pure score ranking and `--per-category` to tune the first-pass category cap.
- Added `Category:` to Markdown report rows.
- Fixed score reason text for future-looking GitHub `pushed_at` values by clamping age days to zero.
- Updated README with diversified query and balanced-report usage.

**Verification:**

- TDD red check: new taxonomy/report tests initially failed because `open_source_scanner.taxonomy` did not exist.
- `uv run pytest -q` -> 58 passed.
- `uv run ruff check src tests` -> all checks passed.
- `uv run oss-scan report --help` shows `--balanced/--global` and `--per-category`.
- Real scan: `uv run oss-scan scan --limit 100 --max-search-requests 10 --min-seconds-between-requests 6` -> 1000 observations from 10 GitHub search requests.
- Recomputed existing SQLite scores after the negative-day fix and regenerated `reports/2026-05-15.md`.
- Verified no `pushed -` text remains in the regenerated report.

**Observed data after scan:**

- Local SQLite contains 1074 unique non-dismissed opportunities.
- Category counts: AI / Agents 417, Infra / DevOps 206, Data / Analytics 176, Developer Tools 110, Security / Privacy 88, Automation / Workflow 43, Web / App Frameworks 18, Productivity / Knowledge 7, Media / Design 5, Commerce / Growth 4.
- Stronger non-AI candidates surfaced include `theonedev/onedev`, `infracost/infracost`, `floci-io/floci`, `openebs/openebs`, `certimate-go/certimate`, `autobase-tech/autobase`, `schemathesis/schemathesis`, `Netflix/maestro`, `apache/incubator-devlake`, `owasp-noir/noir`, `Samsung/CredSweeper`, and `openmeterio/openmeter`.

**Commit:**

- `f569eb9 feat: diversify opportunity reports` pushed to `origin/main`.

**Follow-up:**

- Add risk/downranking rules for gray-area projects such as browser anti-detection, account automation, game idling, free-key lists, and other ToS-sensitive tools.
- Generate memos for a small non-AI shortlist once the risk filter is in place.
