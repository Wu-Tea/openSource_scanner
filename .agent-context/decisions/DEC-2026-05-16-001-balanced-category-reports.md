# DEC-2026-05-16-001: Balanced Category Reports

## Status

accepted

## Date

2026-05-16

## Confirmed By

User feedback noted that the observed report was almost entirely AI-related; prior autonomous-development authorization allowed implementation without a separate approval gate.

## Related Sessions

- 2026-05-16 diversified category reporting

## Related Files

- `config/sources.yml`
- `src/open_source_scanner/taxonomy.py`
- `src/open_source_scanner/__main__.py`
- `src/open_source_scanner/report.py`
- `.agent-context/session-log.md`

## Supersedes

- None

## Superseded By

- None

## Context

The scanner's first real candidate review over-emphasized AI because the source queries included `topic:ai`, `topic:rag`, and `topic:mcp`, while packaging signals such as API, deploy, and hosted also favored current AI tooling projects. The user's goal is broader: find open-source projects that can later be packaged into monetizable products, services, templates, deployment kits, integrations, localization, or support offers.

## Decision

Default reports will use category-balanced ranking instead of pure global score ranking. The source query portfolio will cover multiple opportunity domains, and `oss-scan report` will include category labels and balance candidates across categories before filling remaining slots by global score. Pure global ranking remains available through `--global`.

## Reasons

- A pure score leaderboard can overfit to one hot ecosystem and hide commercially useful projects in other domains.
- Balanced reports support exploration across infrastructure, DevOps, security, data, developer tools, automation, and AI without discarding high-scoring items.
- Category classification can be computed from existing row metadata, avoiding a SQLite migration.
- Keeping `--global` preserves the old behavior for debugging and score-model comparison.

## Rejected Alternatives

- Remove AI entirely: rejected because AI projects can still be valuable, but they should not dominate discovery.
- Create separate reports per query only: rejected because it fragments review and makes cross-domain comparison harder.
- Add a database category column immediately: rejected because the category taxonomy is early and likely to evolve.

## Evidence

- The local database after the diversified scan contains 1074 unique non-dismissed opportunities across ten categories.
- The regenerated report includes non-AI projects near the top, including infrastructure, data, developer tools, automation, security, and commerce candidates.
- Verification passed with `uv run pytest -q` and `uv run ruff check src tests`.

## Consequences

- The top report is now better for discovery, but the classifier is heuristic and may misclassify edge cases.
- The next quality improvement should add risk/downranking rules for gray-area projects that currently score well due to stars, activity, and permissive licenses.
- Category distribution should be monitored after additional scans to tune query ordering and category caps.

## Review Triggers

- One category again dominates the top report after several runs.
- The user wants to prioritize a specific market or exclude AI from a particular report.
- The classifier causes repeated incorrect packaging decisions.
