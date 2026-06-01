# Handoff

## Current Objective

Build `openSource_scanner`: a local-first opportunity radar for finding solo-developer-friendly 2C entertainment, companion, toy, and lightweight consumer products with packaging or small-hit potential.

## Current State

- Repository `https://github.com/Wu-Tea/openSource_scanner.git` has been cloned into `E:\AI\resp_scanner`.
- Implementation plan is saved at `docs/superpowers/plans/2026-05-15-open-source-opportunity-scanner.md`.
- GitHub-only MVP is implemented on `main`: config, GitHub connector, normalizer, scoring, SQLite storage, Markdown reports, Typer CLI, README, and workflow docs.
- Scheduled automation is implemented: GitHub Actions daily scan/report workflow and local Windows helper script.
- Final local verification passed: `uv run pytest -v` -> 25 passed; `uv run ruff check src tests` -> all checks passed; PowerShell parser check for `scripts/run-daily-scan.ps1` passed.
- First small real scan/report verification succeeded with `--limit 1`; generated data was inspected and then removed.
- Opportunity memo workflow is implemented and verified: `oss-scan memo SOURCE SOURCE_ID` writes Chinese review memos under `memos/` and protects existing files unless `--force` is used.
- Shortlist pipeline is implemented and verified: `oss-scan shortlist` groups `package`, `watch`, and `saved` opportunities into a Markdown pipeline view.
- GitHub scan safety controls are implemented: per-run request budget, request spacing, rate-limit state capture, rate-limit floor stop, and fail-closed safety config validation.
- Multi-category opportunity reporting is implemented and pushed in commit `f569eb9`: default GitHub queries now cover developer tools, infra, automation, DevOps, security, monitoring, data, analytics, CLI, and a capped AI query.
- `oss-scan report` now defaults to balanced category output with `--balanced/--global` and `--per-category`; reports include `Category:` for each opportunity.
- A scoring edge case is fixed: future-looking GitHub `pushed_at` timestamps are displayed as `pushed 0 days ago`, not negative days.
- Latest multi-round scan ran on 2026-05-18 across 30 extra GitHub search queries with 7-second spacing; it stored 1904 observations across infra/devops, security/data, and product/business/media themes.
- Latest generated report: `reports/2026-05-18.md` with `--limit 160 --per-category 8`.
- Local SQLite now contains 2951 unique non-dismissed opportunities; category distribution is approximately Infra / DevOps 740, AI / Agents 628, Data / Analytics 406, Security / Privacy 294, Developer Tools 266, Web / App Frameworks 121, Productivity / Knowledge 117, Automation / Workflow 113, Other 93, Media / Design 89, Commerce / Growth 84.
- Latest vertical-pain scan ran on 2026-05-18 across 39 extra GitHub search queries with 7-second spacing; it stored 1050 observations across small-business ops, industry/profession verticals, small pain-point tools, and everyday personal/team utilities.
- Local SQLite now contains 3826 unique non-dismissed opportunities after the vertical scan, a net increase of 875 from the prior baseline. New vertical buckets: Forms & Docs 326, Business Ops 305, Events & Membership 56, Education 51, Finance & Billing 40, Healthcare 36, Real Estate 29, Knowledge & Notes 19, Support & Service 12.
- Vertical-focus report mode is implemented and verified: `oss-scan report --focus vertical` boosts explicit small-business/domain workflows and downranks generic web frameworks, component libraries, AI, infra, developer-tool repos, awesome lists, helper libraries, examples, paper/survey repos, and other non-product false positives.
- Latest focused vertical scan ran on 2026-05-19 across 28 GitHub search queries with 7-second spacing; it stored 184 observations around local services, booking, retail/POS/inventory, invoices, forms, events, membership, rentals, maintenance, tenant portals, and helpdesk/customer portals.
- Local SQLite now contains 3985 unique non-dismissed opportunities after the focused vertical scan, a net increase of 159 from the prior baseline. New vertical buckets include Booking / Scheduling 34, Forms / Surveys / Documents 33, Inventory / Assets / Field Ops 31, Events / Membership 20, Healthcare / Clinic 14, CRM / Sales / Support 4, Finance / Billing 4, Real Estate / Property 4, and Restaurant / Hospitality 2.
- Latest generated vertical report: `reports/2026-05-19.md` from `uv run oss-scan report --today --focus vertical --limit 160 --output-dir reports`.
- Deep research direction memo is saved at `docs/research/2026-05-19-deep-research-direction.md`. It reframes the product around service-led workflow businesses with existing budget, dirty repeated work, and high error cost.
- Latest workflow-family scan ran on 2026-05-19 across 55 GitHub search requests with 7-second spacing. It added 430 observations and 396 net-new unique opportunities, bringing local SQLite to 4381 unique non-dismissed opportunities.
- Workflow scan candidates worth memo review include `kutcode/trustreply`, `BuildSphere-dev/OPTIBIDS`, `JakeLeoDev/proposit`, `monte-carlo-data/transparent-trust`, `FlowEngine-cloud/flowengine`, `Vibra-Labs/Atrium`, `parthg-cmyk/Vendor-Portal-Purchase-Automation-System`, `AmanuelZ/govstack-bb-registration-et`, `amohamed369/perm`, `auxilium-software/auxilium-portal`, and `UnicisTech/unicis-platform-ce`.
- Fragmented waiting-time games memo is saved at `docs/research/2026-05-20-fragmented-waiting-time-games.md`. It records `Desktop Expedition Sticker RPG` as a separate side-experiment track for AI-era delegate/wait/review work rhythms, not a replacement for the B2B workflow scanner.
- User corrected the strategic target on 2026-05-20: as a solo developer, heavy B2B workflow opportunities are not the best default. The new default should prioritize 2C entertainment, companion products, browser toys, creator toys, and consumer micro-products with small-hit potential.
- Solo-developer 2C pivot memo is saved at `docs/research/2026-05-20-solo-dev-2c-entertainment-pivot.md`; accepted decision is recorded in `.agent-context/decisions/DEC-2026-05-20-001-solo-dev-2c-mainline.md`.
- User banned ERP-related applications from default scans on 2026-05-20. Accepted decision is recorded in `.agent-context/decisions/DEC-2026-05-20-002-ban-erp-from-default-scans.md`.
- Latest consumer scan ran on 2026-05-20 using three GitHub query rounds with ERP topic exclusions: desktop companion/idle, browser toy/generator, and lightweight game genres. It stored 293 unique rows in ignored local DB `data/consumer-2026-05-20.sqlite`; result-level word-boundary ERP/B2B filtering left 292 scored non-ERP rows. Generated local report: `reports/2026-05-20-consumer-scan.md`.
- Best candidates from the consumer scan include `Shellishack/vibebud`, `scorzy/IdleAnt`, `georapbox/meme-generator`, `Auwuua/DockCat`, `M-SRIKAR-VARDHAN/MAX-Desktop-Companion`, `Shpigford/society-fail`, `entibo/taipingu`, `cwtickle/danoniplus`, and `MemeCrafters/meme-generator`.
- Recurring automation `market-pain-radar` is ACTIVE. It runs about every 3 hours in `E:\AI\resp_scanner`, scans public communities and GitHub/open-source sources for market pain signals, excludes ERP/heavy enterprise software, and writes records under `records/market-pain/`.
- Automation workflow documentation is saved at `docs/automation/market-pain-radar.md`; record directory index is `records/market-pain/index.md`.
- User authorized autonomous ongoing development with worktree-based subagent delegation.

## Next Action

Monitor `records/market-pain/` as the new recurring research feed. Next product feature should add a `consumer` / `2c` focus mode, consumer-hit taxonomy, query packs for desktop companions, cozy idle/incremental games, browser toys, meme/generator tools, creator toys, avatar/personalization tools, focus buddies, and low-scope narrative/horror/puzzle experiments, plus a first-class exclusion list for ERP/B2B terms. B2B workflow-family scoring should remain available as a secondary lens, not the default mainline.

## Blockers

- None currently known.

## Active Questions

- None requiring user input due current autonomous-development authorization.

## Relevant Decisions

- `.agent-context/decisions/DEC-2026-05-15-001-v1-github-local-mvp.md`
- `.agent-context/decisions/DEC-2026-05-16-001-balanced-category-reports.md`
- `.agent-context/decisions/DEC-2026-05-20-001-solo-dev-2c-mainline.md`
- `.agent-context/decisions/DEC-2026-05-20-002-ban-erp-from-default-scans.md`

## Files To Read First

- `docs/superpowers/plans/2026-05-15-open-source-opportunity-scanner.md`
- `docs/research/2026-05-20-solo-dev-2c-entertainment-pivot.md`
- `docs/research/2026-05-20-fragmented-waiting-time-games.md`
- `docs/automation/market-pain-radar.md`
- `docs/research/2026-05-19-deep-research-direction.md`
- `.agent-context/session-log.md`
- `.agent-context/decisions/DEC-2026-05-15-001-v1-github-local-mvp.md`
- `.agent-context/archive/session-log-2026-05-15-pre-compaction.md` only if deeper pre-compaction detail is needed

## Do Not Reopen Unless Needed

- No archived context yet.

## Notes

- Do not commit secrets such as `GITHUB_TOKEN`, cookies, API keys, or private user data.
- The workspace is Windows/PowerShell. Use Windows-compatible commands and libraries by default; avoid Unix-only shell syntax such as `python <<'PY'`.
- Re-check this handoff if repository state diverges from the plan or if a worktree merge fails.
