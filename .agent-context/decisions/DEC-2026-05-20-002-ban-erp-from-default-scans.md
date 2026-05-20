# DEC-2026-05-20-002: Ban ERP From Default Opportunity Scans

## Status

accepted

## Date

2026-05-20

## Confirmed By

User explicitly requested: "禁止扫描ERP相关应用".

## Related Sessions

- 2026-05-20 solo-developer 2C target correction
- 2026-05-20 consumer scan with ERP exclusion

## Related Files

- `config/consumer-round-1/sources.yml`
- `config/consumer-round-2/sources.yml`
- `config/consumer-round-3/sources.yml`
- `reports/2026-05-20-consumer-scan.md`
- `.agent-context/session-log.md`
- `.agent-context/handoff.md`

## Supersedes

- None

## Superseded By

- None

## Context

The project target has shifted toward solo-developer-friendly 2C entertainment, companion products, browser toys, creator toys, and lightweight consumer products. ERP and adjacent enterprise operations software pull the scanner back toward heavy B2B implementation work, which no longer matches the default target.

## Decision

Default opportunity scans must exclude ERP-related applications and adjacent enterprise operations categories.

ERP-related exclusions include, at minimum:

- ERP
- enterprise resource planning
- Odoo
- SAP
- accounting suites
- invoice/invoicing systems
- inventory/warehouse management
- CRM
- POS
- Salesforce
- NetSuite
- procurement

Use both query-level exclusions where possible and result-level text filtering before recommending candidates.

## Reasons

- ERP opportunities are usually sales-heavy, integration-heavy, support-heavy, and operationally complex.
- They bias results toward B2B workflows, which the user has rejected as the default route.
- Even if open-source ERP projects have monetization potential, they are not well matched to solo 2C small-hit exploration.

## Rejected Alternatives

- Keep ERP but lower its score: rejected because the user requested a ban, not a soft downrank.
- Only filter exact `erp`: rejected because many ERP-adjacent results use product names or adjacent categories such as accounting, inventory, CRM, POS, or procurement.
- Delete old ERP/B2B scan history: rejected because historical data can remain archived as long as it is not treated as the default feed.

## Evidence

- The 2026-05-20 consumer scan used GitHub topic-level exclusions and result-level ERP/B2B filtering.
- The scan report recorded one precise ERP/B2B match after word-boundary filtering, while preserving consumer/game candidates that were previously false positives under substring matching.

## Consequences

- Future scanner code should add a first-class exclusion list rather than relying only on query syntax and ad hoc report filtering.
- B2B and ERP data may remain in the database but should be hidden from default consumer reports.

## Review Triggers

- User explicitly asks to run a B2B or ERP-specific scan.
- A lightweight non-ERP consumer product accidentally uses one of the blocked words and needs a scoped exception.
