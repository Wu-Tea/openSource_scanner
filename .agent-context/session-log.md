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

### 2026-05-16 - Full configured query scan

**Goal:** Run another discovery pass after diversifying the query portfolio, including the previously unscanned no-code, productivity, and API queries.

**What ran:**

- Baseline before scan: 1074 unique opportunities in `data/scanner.sqlite`.
- Command: `uv run oss-scan scan --limit 100 --max-search-requests 13 --min-seconds-between-requests 6`.
- Result: 1300 observations from 13 GitHub search requests.
- Regenerated report: `uv run oss-scan report --today --limit 120 --per-category 6`.

**Observed data after scan:**

- Local SQLite contains 1336 unique non-dismissed opportunities, a net increase of 262.
- Category counts: AI / Agents 477, Infra / DevOps 217, Data / Analytics 189, Developer Tools 174, Automation / Workflow 96, Security / Privacy 95, Productivity / Knowledge 44, Web / App Frameworks 30, Media / Design 10, Commerce / Growth 4.
- Newly surfaced or newly prominent non-AI candidates include `dokku/dokku`, `mswjs/msw`, `gotenberg/gotenberg`, `Volmarg/personal-management-system`, `nocode-js/sequential-workflow-designer`, `standard-webhooks/standard-webhooks`, `git-town/git-town`, `muety/wakapi`, and `super-productivity/super-productivity`.

**Manual spot checks:**

- Official GitHub pages were opened for `dokku/dokku`, `mswjs/msw`, `gotenberg/gotenberg`, `Volmarg/personal-management-system`, `nocode-js/sequential-workflow-designer`, and `standard-webhooks/standard-webhooks`.
- The checks confirmed the broadening effect: the candidate set now includes PaaS, API mocking, document conversion API, no-code workflow UI, webhook standards/tooling, and personal management software.

**Follow-up:**

- Add risk/downranking rules before marking candidates, because high scores still include some platform-ToS-sensitive automation and anti-detection projects.
- Generate memos for the top safe non-AI candidates after risk filtering.

### 2026-05-18 - Multi-round broad discovery scan

**Goal:** Run several additional GitHub discovery rounds to find stronger non-AI and packaging-friendly projects.

**What ran:**

- Baseline before scan: 1336 unique opportunities in `data/scanner.sqlite`.
- Round 1: 10 infra/devops queries covering PaaS, platform engineering, Kubernetes dashboards, Terraform, observability, backup, reverse proxy, homelab, Docker Compose, and FinOps.
- Round 2: 10 security/data queries covering AppSec, vulnerability scanners, SAST, secret scanning, IAM, zero trust, data visualization, ETL, workflow orchestration, and data quality.
- Round 3: 10 product/business/media queries covering billing, usage-based billing, webhooks, API gateway, PDF, knowledge base, helpdesk, CRM, UI builder, and design systems.
- Each query used 7-second spacing and stopped well above the configured rate-limit floor.
- Total observations: 1904 from 30 GitHub search requests.
- Regenerated report: `uv run oss-scan report --today --limit 160 --per-category 8`, output `reports/2026-05-18.md`.

**Observed data after scan:**

- Local SQLite contains 2951 unique non-dismissed opportunities, a net increase of 1615.
- Category counts: Infra / DevOps 740, AI / Agents 628, Data / Analytics 406, Security / Privacy 294, Developer Tools 266, Web / App Frameworks 121, Productivity / Knowledge 117, Automation / Workflow 113, Other 93, Media / Design 89, Commerce / Growth 84.
- Newly surfaced high-score candidates include `databasus/databasus`, `krayin/laravel-crm`, `uselotus/lotus`, `dromara/MaxKey`, `krakend/krakend-ce`, `skyhook-io/radar`, `wiredoor/wiredoor`, `DDULDDUCK/every-pdf`, `LibPDF-js/core`, `openappsec/openappsec`, `cloudsplaining`, `policy_sentry`, `databasus/databasus`, `gobackup/gobackup`, and `community-scripts/ProxmoxVE`.

**Candidate-quality notes:**

- Best packaging-friendly areas surfaced: database backup/restore, IAM/SSO, API gateway/webhooks, PDF/document tooling, CRM/billing, Kubernetes/self-hosted operations, and security reporting.
- The scan also surfaced noisy high-score items such as vulnerable lab environments, crawler/scraper frameworks, anti-detection/browser automation, and platform-specific automation; those need risk/downranking before shortlist automation.

**Follow-up:**

- Add explicit risk labels/downranking for vulnerable labs, scraper/crawler/proxy-rotation projects, account/platform automation, and offensive-only security collections.
- Generate memos for the strongest safe candidates after applying the risk filter.

### 2026-05-18 - Vertical pain-point discovery scan

**Goal:** Reorient discovery away from geek/professional infrastructure and toward vertical solutions or small-scope pain points that could be packaged for less technical users.

**What ran:**

- Baseline before scan: 2951 unique opportunities in `data/scanner.sqlite`.
- Round 1: small-business operations queries covering inventory, POS, restaurants, hotels, property management, booking, appointments, scheduling, invoice management, and order management.
- Round 2: industry/profession vertical queries covering school/LMS, clinic/hospital, dental, veterinary, law firm, real estate, gym, and membership management.
- Round 3: small pain-point tool queries covering ticketing, helpdesk, events, form builder, surveys, document management, knowledge base, asset management, maintenance, and field service.
- Round 4: everyday utility queries covering spreadsheets, resume builders, contract management, receipt scanning, QR menu, employee scheduling, calendar apps, rental management, and personal finance. The run stopped at the configured rate-limit floor before expense tracking.
- Total observations: 1050 across 39 GitHub search requests.
- Regenerated report: `uv run oss-scan report --today --limit 180 --per-category 10`.

**Observed data after scan:**

- Local SQLite contains 3826 unique non-dismissed opportunities, a net increase of 875.
- New vertical-oriented buckets from the ad hoc classifier: Forms & Docs 326, Business Ops 305, Events & Membership 56, Education 51, Finance & Billing 40, Healthcare 36, Real Estate 29, Knowledge & Notes 19, Support & Service 12.
- Stronger vertical/small-pain candidates include `TDuckCloud/tduck-survey-form`, `tastyigniter/TastyIgniter`, `mighty840/kitchenasty`, `evangauer/openvpm`, `microrealestate/microrealestate`, `krayin/laravel-crm`, `MicroPyramid/Django-CRM`, `OpenReservation/OpenReservation`, `classiebit/eventmie`, `simonwep/ocular`, `RIP-Comm/sossoldi`, `hisabi-app/hisabi`, `sw-carlos-cristobal/sharetab`, `dadaloop82/EverShelf`, `FOSSBilling/FOSSBilling`, `amruthpillai/reactive-resume`, and `LingyiChen-AI/JadeAI`.

**Candidate-quality notes:**

- The default technical scoring still over-ranks generic frameworks and infrastructure when vertical projects have fewer stars or fewer deployment keywords.
- A vertical-opportunity tagger/report is needed so target-user pain points such as restaurant ordering, veterinary practice management, rental management, forms/surveys, booking, and personal finance are visible without manual filtering.

**Follow-up:**

- Implement a vertical report mode or scoring overlay that prioritizes explicit target users and domain workflows over generic technical popularity.
- Generate memos for a small set of vertical candidates after adding the overlay.

### 2026-05-19 - Vertical report mode and focused small-tool scan

**Goal:** Continue scanning with lower weight for generic web development frameworks and higher visibility for vertical business workflows or small tools that solve narrow operational pain points.

**What changed:**

- Added `--focus vertical` to `oss-scan report`.
- Added a vertical classifier and ranking overlay that boosts explicit business/domain workflows such as appointments, forms, invoices, rentals, volunteer management, property management, clinics, education, inventory, POS, field ops, and helpdesk/customer portals.
- Added penalties for generic web/app frameworks, component libraries, generic AI/infra/developer-tool repos, awesome lists, helper libraries, example repos, paper/survey repos, and false-positive terms such as event buses or generic framework routing when no real business workflow is present.
- Updated README usage examples for vertical opportunity reports.

**Verification:**

- TDD red check: targeted taxonomy/report tests initially failed because `classify_vertical_row` did not exist.
- `uv run pytest tests/test_taxonomy.py tests/test_cli.py::test_report_command_vertical_focus_prioritizes_business_pain_points -q` -> 7 passed after implementation.
- Added a regression test for generic event-framework false positives.
- `uv run pytest -q` -> 66 passed.
- `uv run ruff check src tests` -> all checks passed.

**What ran:**

- Baseline before focused scan: 3826 unique non-dismissed opportunities.
- Round 1: local-service queries covering salon/barber/spa/clinic/dental/tutor/class/daycare booking and management. It stopped at the configured GitHub rate-limit floor after the daycare query.
- Round 2: retail/finance queries covering retail POS, barcode inventory, warehouse inventory, rental management, equipment rental, repair shop management, invoices, receipt OCR, quote generation, and small-business accounting.
- Round 3: forms/service queries covering self-hosted forms and surveys, document and contract generation, event ticketing, membership directories, volunteer management, maintenance requests, tenant portals, and customer portals/helpdesk.
- Total observations: 184 across 28 GitHub search requests with 7-second spacing.
- Regenerated vertical report: `uv run oss-scan report --today --focus vertical --limit 160 --output-dir reports`, output `reports/2026-05-19.md`.

**Observed data after scan:**

- Local SQLite contains 3985 unique non-dismissed opportunities, a net increase of 159.
- New vertical buckets: Booking / Scheduling 34, Forms / Surveys / Documents 33, Inventory / Assets / Field Ops 31, Events / Membership 20, Healthcare / Clinic 14, Other 13, CRM / Sales / Support 4, Finance / Billing 4, Real Estate / Property 4, Restaurant / Hospitality 2.
- Promising newly surfaced candidates include `akira-io/laravel-pdf-invoices`, `angelodlfrtr/go-invoice-generator`, `H1D/easypdf-lite`, `Anmol-Baranwal/form-builder`, `ICodingStack/ContractSpark`, `rubyforgood/casa`, `GTBitsOfGood/VolunTrack`, `aerogear/OpenVolunteerPlatform`, `vereinfacht/vereinfacht`, `yuriycto/AcumaticaInventoryScanner`, `ChanMeng666/automotive-repair-management-system`, `omarbadrani/TunisiashopERP---Complete-Retail-Management-System`, `nbt4/rentalcore`, `BEKO2210/Prepper_Log`, `elghaied/payload-reserve`, `OthmanAdi/BarbersBuddies_Onlineshop_maker`, `ayyub-humeid/real-estate-system`, `MohamedShiras/Serendib`, and `UCDS/health4all_v3`.

**Candidate-quality notes:**

- The vertical overlay materially reduces generic web framework dominance. It now also avoids broad "event", "spa", and "knowledge base" false positives that previously elevated event-study papers, single-page-app topics, and personal note tools.
- Best near-term packaging lanes are document/invoice generation, form builders, volunteer/membership management, inventory/POS/repair shop management, rentals/tenant portals, appointment booking, and niche healthcare/clinic tools.
- Repos with missing or restrictive licenses, demo/sample positioning, platform-automation risk, or unclear maintenance should be filtered before memo generation.

**Follow-up:**

- Add a `--min-vertical-score` or `--vertical-only` filter so reports can exclude weak vertical matches entirely.
- Generate memos for 8-12 top vertical candidates, starting with document/invoice generation, volunteer management, inventory/repair, booking, property management, and clinic/vet workflows.

### 2026-05-19 - Deep research report synthesis

**Goal:** Study `D:\Downloads\deep-research-report (11).md` and turn it into project direction for future scanning.

**What changed:**

- Added `docs/research/2026-05-19-deep-research-direction.md`.
- Captured the report's central filter: prioritize workflows with existing budget, dirty repeated work, high error cost, and a service-to-software path.
- Translated the report into scanner implications: new workflow families, search query packs, scoring signals, downranking rules, and next product changes.

**Direction captured:**

- Highest-priority workflow families are RFP/proposal/security-questionnaire response, agency/client-delivery OS, permit/license/inspection renewal tracking, vendor compliance/COI/credential tracking, accounting/tax client portals, trust center lite, chargeback evidence builders, construction permit/submittal workflows, and niche professional-service client portals.
- The scanner should evolve from broad vertical nouns toward workflow-family scoring that asks who pays, what manual process is replaced, and what error is costly.

**Follow-up:**

- Implement workflow-family taxonomy and `--focus workflow`.
- Add score reasons for workflow signals such as renewal, expiration, owner approval, document chase, evidence packet, and export format.
- Add risk filtering for platform automation, demo/sample repos, library-only repos, and unknown-license repos before memo generation.

### 2026-05-19 - Workflow-family discovery scan

**Goal:** Run several GitHub scans based on the deep-research direction: existing-budget, dirty-workflow, high-error-cost opportunities instead of generic vertical nouns.

**What ran:**

- Baseline before scan: 3985 unique non-dismissed opportunities.
- Strict report-keyword pass: 24 GitHub search requests across RFP/security response, agency delivery, permits/vendor compliance, and finance/professional workflows. It added 19 observations and 19 net-new unique opportunities. Many exact phrase queries returned zero results, especially permit, COI, tax portal, and construction submittal phrases.
- Broader workflow-language pass: 31 GitHub search requests across proposal/tender/bid management, client portals/document chasing, vendor/supplier/credential/permit operations, and dispute/professional workflows. It added 411 observations and 377 net-new unique opportunities.
- Final local SQLite total: 4381 unique non-dismissed opportunities.
- Regenerated `reports/2026-05-19.md` with `uv run oss-scan report --today --focus vertical --limit 220 --output-dir reports`.

**Observed workflow buckets from new rows:**

- RFP / Proposal / Security Questionnaire: 106 heuristic matches.
- Vendor Compliance / COI / Credentials: 87 heuristic matches.
- Accounting / Tax / AP / Documents: 76 heuristic matches.
- Permits / Licenses / Inspections: 19 heuristic matches.
- Agency / Client Delivery / Change Orders: 14 heuristic matches.
- Chargeback / Dispute Evidence: 7 heuristic matches.
- Professional Service Client Portals: 4 heuristic matches.

**Promising candidates:**

- `kutcode/trustreply` - open-source questionnaire response automation for vendor, security, privacy, compliance, and due-diligence workflows.
- `BuildSphere-dev/OPTIBIDS` - B2B AI-driven RFP and tender-management workflow; very aligned but young.
- `JakeLeoDev/proposit` - self-hosted proposal management with multi-tenancy, AI, PDF export, and public sharing.
- `monte-carlo-data/transparent-trust` - RFP/security questionnaire/compliance document answering with transparency positioning.
- `FlowEngine-cloud/flowengine` - white-label client portal for automation agencies; potentially strong agency-delivery wedge but license needs review.
- `Vibra-Labs/Atrium` - self-hosted agency/freelancer client portal; license appears restrictive and needs review.
- `parthg-cmyk/Vendor-Portal-Purchase-Automation-System` and `7007259Ankur/vendor-onboarding-portal` - vendor onboarding and approval workflows.
- `AmanuelZ/govstack-bb-registration-et` - business registration and trade-license renewal reference implementation; useful permit/license signal but country-specific.
- `amohamed369/perm` - PERM immigration case-management tracker; very niche professional-service portal signal.
- `auxilium-software/auxilium-portal` - CRM and case-management portal for charities and third-sector organisations.
- `UnicisTech/unicis-platform-ce` - open-source GRC platform; broader than ideal but aligned with compliance workspace thesis.

**Quality notes:**

- Exact workflow phrases are too sparse on GitHub; broader operational words produce better recall but introduce many false positives.
- Current vertical report does not yet surface the best workflow-family finds because they often have low stars and narrow descriptions. This confirms the need for a dedicated workflow-family scoring layer.
- Permit/license/COI/chargeback opportunities seem less represented as mature open-source products; these may be better found through adjacent building blocks, commercial competitor research, or service-led validation rather than GitHub stars alone.

**Follow-up:**

- Implement workflow-family taxonomy and `--focus workflow`; the scan results provide test fixtures.
- Add risk labels for library-only, SDK/API-client, demo/sample, restrictive-license, platform automation, and speculative AI agent projects.
- Write memos for `trustreply`, `OPTIBIDS`, `proposit`, `transparent-trust`, `flowengine`, `Atrium`, `PERM Tracker`, and one vendor-onboarding candidate.

### 2026-05-20 - Fragmented waiting-time games report synthesis

**Goal:** Study `D:\Downloads\deep-research-report (12).md` and decide how it should influence the opportunity radar.

**What changed:**

- Added `docs/research/2026-05-20-fragmented-waiting-time-games.md`.
- Captured the report's thesis: AI-era delegate/wait/review loops create repeated fragmented waiting windows that may support a desktop-first passive-active game.
- Recorded the recommended MVP direction: `Desktop Expedition Sticker RPG`, a Windows-first bottom-of-screen settlement and expedition game with passive progress and 30-90 second active choices.
- Spot-checked current public examples and infrastructure signals: Codex-style background/parallel agent work, `Rusty's Retirement`, `Ropuka's Idle Island`, and `Desktop Survivors 98`.

**Direction captured:**

- Treat this as a side experiment, not a replacement for the main B2B workflow scanner.
- Validate by co-working retention rather than raw playtime: D1/D7 return, background-open minutes, interventions per hour, and whether users keep it open during real work.
- If pursued, use a separate prototype/research lane so game-specific signals do not dilute workflow-family scoring.

**Follow-up:**

- Keep workflow-family taxonomy and risk scoring as the mainline scanner work.
- If the user chooses the game path, create a separate prototype repo and 30-day MVP plan for the Desktop Expedition Sticker RPG.

### 2026-05-20 - Solo-developer 2C target correction

**Goal:** Correct the scanner's strategic target after user feedback that heavy B2B workflow opportunities are poorly matched to a solo developer.

**What changed:**

- Added `docs/research/2026-05-20-solo-dev-2c-entertainment-pivot.md`.
- Added accepted decision `.agent-context/decisions/DEC-2026-05-20-001-solo-dev-2c-mainline.md`.
- Updated `handoff.md` so future work treats 2C entertainment, companion products, browser toys, creator toys, and consumer micro-products as the default mainline.

**Direction captured:**

- The previous scans drifted because GitHub, stars, deployment keywords, workflow language, and vertical business nouns bias discovery toward B2B/SaaS/tooling.
- For this user, the better default is solo-developer scope: fast prototypes, strong visual hook, shareability, product-led distribution, and small-hit potential.
- The desktop waiting-time game thesis should be promoted from side experiment to the first 2C validation lane.

**Follow-up:**

- Add a `consumer` / `2c` report focus.
- Add consumer-hit taxonomy and scoring.
- Add query packs and future collectors for Steam, itch.io, Product Hunt, Reddit, Xiaohongshu/TikTok-style social signals, and GitHub implementation references.
