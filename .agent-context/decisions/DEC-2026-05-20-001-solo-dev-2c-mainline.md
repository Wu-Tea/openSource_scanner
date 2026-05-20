# DEC-2026-05-20-001: Shift Main Opportunity Target To Solo-Developer 2C Products

## Status

accepted

## Date

2026-05-20

## Confirmed By

User explicitly corrected the target: as a solo developer, B2B workflow opportunities are too heavy, and a 2C entertainment small-hit direction is likely better.

## Related Sessions

- 2026-05-20 fragmented waiting-time games report synthesis
- 2026-05-20 solo-developer 2C pivot

## Related Files

- `docs/research/2026-05-20-fragmented-waiting-time-games.md`
- `docs/research/2026-05-20-solo-dev-2c-entertainment-pivot.md`
- `.agent-context/session-log.md`
- `.agent-context/handoff.md`

## Supersedes

- The prior assumption that B2B workflow-family scanning should remain the mainline.

## Superseded By

- None

## Context

The scanner initially moved from broad open-source packaging toward vertical B2B workflow opportunities. That direction is commercially rational for small service teams, but it overfits the wrong operator profile for this project. A solo developer usually has less capacity for sales, implementation, support, compliance, onboarding, and domain-specific service delivery.

The newest research report on fragmented waiting-time games introduced a more solo-developer-compatible opportunity: a desktop-first, passive-active entertainment product for AI-era waiting loops.

## Decision

The scanner's default strategic target should shift toward 2C entertainment, companion products, browser toys, creator toys, and other consumer micro-products that a solo developer can prototype, polish, distribute, and test quickly.

B2B workflow scanning remains available as a secondary lens, but it should no longer define the default next action.

## Reasons

- A 2C entertainment or playful utility product can be validated with a prototype, demo, trailer, or small launch more quickly than a B2B workflow product.
- Solo developers are usually better matched to product-led distribution than sales-led B2B implementation.
- GitHub-only scanning is structurally biased toward technical and business tooling, so the scanner must expand toward consumer platforms and social signals.
- The desktop waiting-time game thesis directly matches current AI-agent work rhythms and has a clear prototype path.

## Rejected Alternatives

- Continue B2B workflow as mainline: rejected because it mismatches solo-developer capacity and keeps search results feeling off-target.
- Abandon GitHub entirely: rejected because GitHub is still useful for templates, engines, abandoned prototypes, and implementation references.
- Chase generic AI consumer wrappers: rejected because they often lack a durable entertainment loop or distribution hook.

## Evidence

- Recent scan outputs overrepresented AI, developer tools, infrastructure, compliance, and workflow products.
- The 2026-05-20 waiting-time games report identifies a consumer entertainment opportunity tied to AI-era waiting loops.
- Public consumer platforms such as Steam and itch.io expose current demand signals that GitHub cannot capture well.

## Consequences

- Next code changes should add a consumer-hit focus mode and reduce the default weight of B2B workflow signals.
- New collectors or import workflows are needed for Steam, itch.io, Product Hunt, Reddit, and short-video/social platforms.
- Existing B2B scan data should be retained but treated as a secondary archive rather than the main decision feed.

## Review Triggers

- Consumer scans fail to surface buildable ideas after several rounds.
- A B2B candidate becomes unusually lightweight and solo-founder friendly.
- The user decides to pursue a service-led B2B business after all.
