# Revenue Pipeline Design Review - 2026-06-01

## Review Scope

Reviewed artifacts:

- `docs/superpowers/specs/2026-06-01-revenue-pipeline-design.md`
- `docs/revenue-pipeline/2026-06-01-spark-implementation-blueprint.md`

Review goal:

Find design failures before implementation, especially failures that would recreate the old problem: many scans, many reports, no selected revenue action.

## Findings

### P0 - Live collectors can distract from the core pipeline

Risk: Spark may start by implementing HN/V2EX/Reddit/itch/Steam collectors. That feels productive but does not prove the revenue pipeline works.

Resolution: V1 implementation should start from `import-record` using the existing 2026-06-01 market-pain record, plus local GitHub opportunity rows. Live collectors are optional later. The first implementation milestone must produce `bets/current.md` and experiment artifacts from local data.

### P0 - The selector must not create multiple active bets

Risk: A scanner naturally wants to list many good ideas. That recreates reading debt and spreads execution thin.

Resolution: Store bet status in SQLite and enforce only one `active` bet. If one active bet exists, `select-bet` writes or updates backlog only. Replacing the active bet requires an explicit kill/pause/review command.

### P1 - Scoring can overfit loud communities

Risk: V2EX, HN, Reddit, and GitHub are builder-heavy. They can make developer-adjacent ideas look stronger than mainstream consumer ideas.

Resolution: The judge must separate evidence volume from distribution fit. A candidate with many forum mentions but no clear consumer channel should fail or score low. Every selected bet must name the first channel and the first 100-user path.

### P1 - Tool matches can be mistaken for product opportunities

Risk: A good GitHub repo may only be an implementation reference. The project can drift back to "package this repo" even when no consumer desire exists.

Resolution: `ToolMatch.match_type` must distinguish product candidate, implementation reference, template, asset, and rejected. The judge should treat tool matches as acceleration points, not demand evidence.

### P1 - Generated experiment docs can become boilerplate

Risk: `plan.md`, `landing-copy.md`, and `distribution-posts.md` can look complete while still being generic.

Resolution: Every experiment artifact must include the selected bet slug, target audience, hook, success criteria, kill criteria, and one concrete channel. A generic artifact should fail tests or self-review.

### P1 - AI summarization can hide evidence quality

Risk: If LLM summarization enters too early, the pipeline may produce confident but unauditable conclusions.

Resolution: V1 should use deterministic Markdown import and rule-based extraction. AI summarization can be a later optional layer only if source URLs, evidence IDs, and confidence remain auditable.

### P2 - The implementation can become too large for one Spark pass

Risk: The full design has many modules. A fast coding model may do better with clear milestones than one huge patch.

Resolution: Follow the commit sequence in the blueprint. Stop after Phase 7 if Phase 8 review logic gets too large; a pipeline that imports, judges, selects, and plans is already useful.

### P2 - Existing generated reports may pollute tests

Risk: The workspace has uncommitted generated reports and records. Tests or import examples might accidentally depend on local dirty files.

Resolution: Tests should use synthetic fixtures under `tests/fixtures/`, not untracked local reports. The real `records/market-pain/2026-06-01-1829.md` can be used for manual smoke testing, not as a required committed fixture unless intentionally added later.

## Rejected Implementation Approaches

### Approach A: Recreate the 3-hour automation first

Rejected because it would restart research-only output before judgment and execution exist.

### Approach B: Build all live collectors first

Rejected because platform rules and data parsing differ by source. The business risk is not lack of data; the business risk is lack of selection and execution.

### Approach C: Add an LLM judge as the core V1

Rejected for V1 because opaque summaries and hallucinated confidence would make debugging hard. A later LLM layer can help write better memos after deterministic evidence and scoring are stable.

### Approach D: Keep using the existing `opportunities` table only

Rejected because repository opportunities are not the same as market pain evidence, product candidates, bets, or experiments. New tables keep the model honest.

## Design Completeness Check

- Current app purpose is defined: local-first revenue pipeline for solo 2C/light consumer bets.
- Existing code integration points are named.
- Non-goals and banned categories are explicit.
- Data model covers evidence, pain, tools, candidates, scores, bets, experiments, and reviews.
- CLI commands are specified.
- Output paths are specified.
- Safety and platform boundaries are specified.
- Acceptance criteria are testable.
- Automation remains disabled.

## Implementation Guardrails

Spark should preserve these invariants:

1. `oss-scan select-bet` can never create two active bets.
2. `oss-scan plan-experiment` refuses to run without an active bet.
3. `oss-scan judge` records hard-gate failures, not just total scores.
4. ERP/B2B bans remain default behavior.
5. Local Markdown import works before live source collectors are attempted.
6. Generated reports are not auto-committed.
7. All command examples remain PowerShell-compatible.

## Reviewer Verdict

Accepted with constraints.

The design is ready for implementation planning as long as the first coding pass focuses on the local-data pipeline:

`import existing record -> extract pain signals -> match local tools -> judge candidates -> select one bet -> write experiment artifacts`

Live collectors and recurring automation should wait.
