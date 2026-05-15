# DEC-2026-05-15-001: V1 GitHub Local MVP

## Status

accepted

## Date

2026-05-15

## Confirmed By

User authorized autonomous implementation after approving the plan direction.

## Related Sessions

- 2026-05-15 repository sync and planning session

## Related Files

- `docs/superpowers/plans/2026-05-15-open-source-opportunity-scanner.md`
- `.agent-context/session-log.md`

## Supersedes

- None

## Superseded By

- None

## Context

The project aims to regularly discover open-source projects that may be suitable for legal and ethical packaging into products, services, templates, localization, deployment kits, integrations, or support offers.

## Decision

V1 will be a local-first Python CLI that scans GitHub repositories, normalizes metadata into opportunities, scores them with explainable rules, stores history and feedback in SQLite, and generates Markdown reports.

## Reasons

- GitHub exposes structured repository metadata that is suitable for an initial scanner.
- A local CLI is easier to verify and schedule than a web app or hosted service.
- Rule-based scoring makes early recommendations inspectable and tunable.
- SQLite provides durable local history without introducing backend infrastructure.
- Markdown reports are easy to read, commit, diff, and refine.

## Rejected Alternatives

- Multi-community crawler in V1: rejected because it would increase noise and integration risk before the scoring model is validated.
- Dashboard-first product: rejected because the core discovery and scoring loop needs to work before UI investment.
- LLM-first scoring: rejected for V1 because it would be harder to debug and tune without a stable data pipeline.

## Evidence

- User stated the goal: find good open-source projects to package and monetize later.
- Plan file already defines the GitHub-only MVP workflow and implementation tasks.
- Repository is empty, making a focused MVP scaffold practical.

## Consequences

- Early work should prioritize connector boundaries, scoring explainability, and report usefulness.
- Additional sources should wait until the GitHub loop produces useful reports.
- License risk must be represented in scoring and report output.

## Review Triggers

- The scanner cannot produce useful GitHub candidates after several runs.
- User wants to prioritize non-GitHub communities.
- Packaging decisions require deeper legal review than simple SPDX filtering.
