# DEC-2026-06-01-001: Make Revenue Pipeline The Mainline

## Status

accepted

## Date

2026-06-01

## Confirmed By

User explicitly said the purpose is to find ways to make money and directly execute, not to fall into research-only or vibecoding drift. User also deleted the standalone `market-pain-radar` automation and agreed it should be recreated only after the pipeline is ready.

## Related Sessions

- 2026-06-01 discussion about AI automated workflow design
- 2026-06-01 market-pain radar smoke run
- 2026-06-01 discussion about avoiding research-only automation and vibecoding drift
- 2026-06-01 context cleanup request

## Related Files

- `.agent-context/handoff.md`
- `.agent-context/session-log.md`
- `docs/automation/market-pain-radar.md`
- `docs/research/2026-05-20-solo-dev-2c-entertainment-pivot.md`
- `.agent-context/decisions/DEC-2026-05-20-001-solo-dev-2c-mainline.md`
- `.agent-context/decisions/DEC-2026-05-20-002-ban-erp-from-default-scans.md`

## Supersedes

- Treating scan volume, research records, or candidate lists as the main deliverable.
- Treating B2B workflow-family opportunities as the default project direction.
- Recreating standalone recurring scan automation before judgment and execution layers exist.

## Superseded By

- None

## Context

The project began as a GitHub/open-source opportunity scanner. It then explored broader categories, B2B vertical workflows, market-pain records, and a recurring `market-pain-radar` automation.

That history created a risk: future sessions could read older context and continue scanning or writing reports without moving toward a concrete product bet. The user clarified that, as a solo developer, heavy B2B opportunities are a poor default and that the project should pursue 2C/light consumer opportunities with packaging and monetization potential.

The user also challenged the workflow itself: a scanner that produces documents still leaves the user doing all judgment and execution. The automation should help choose and execute a revenue path, not just collect information.

## Decision

The project mainline is now a Revenue Pipeline.

Default work should move from raw discovery to a complete chain:

`public pain signals -> opportunity judge -> bet selector -> experiment plan -> execution artifacts -> revenue review`

The expected output is one active revenue bet at a time, with concrete validation and execution steps. Scans, reports, records, and GitHub matches are inputs into that decision process.

## Reasons

- The user wants a path toward monetization, not a larger reading queue.
- Solo-developer execution benefits from narrowing to one bet with a validation plan.
- Research-only automation can create the feeling of progress while avoiding shipping, distribution, pricing, and feedback.
- The existing scanner is useful as an input layer, but it needs judgment and execution layers to become operational.
- The 2C/light consumer direction better matches solo-developer packaging, small launches, demos, and playful distribution loops.

## Rejected Alternatives

- Keep running broad scans and reports: rejected because it adds reading debt without choosing what to build.
- Recreate `market-pain-radar` immediately: rejected because it would restart research-only automation before the pipeline is ready.
- Return to B2B workflow/ERP opportunities by default: rejected because it conflicts with the solo-developer 2C direction and ERP ban.
- Build many prototypes in parallel: rejected because it increases vibecoding drift and makes validation unclear.

## Evidence

- The user explicitly corrected the strategic target to solo-developer 2C/light consumer products on 2026-05-20.
- The user explicitly banned ERP-related applications from default scans on 2026-05-20.
- The 2026-06-01 market-pain smoke run produced useful themes but still required manual reading and judgment.
- The user deleted the standalone automation and asked to wait until the pipeline is ready.

## Consequences

- Next implementation should prioritize `opportunity-judge`, `bet-selector`, experiment planning, and revenue review.
- New recurring automation should not be created until it can produce action-oriented outputs.
- Future handoffs should keep old B2B/workflow scan history out of the current objective.
- Generated market-pain records and reports can remain as data, but they should not define the next action by themselves.

## Review Triggers

- User explicitly asks to return to B2B, ERP, or service-led workflow opportunities.
- User explicitly asks for research-only scanning or reporting.
- Several 2C/light consumer bets fail and the user wants to reassess the strategic direction.
- The first Revenue Pipeline implementation reveals that another structure would choose and execute bets more reliably.
