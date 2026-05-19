# Deep Research Direction Memo - 2026-05-19

Source report: `D:\Downloads\deep-research-report (11).md`

## Overview

The report argues that a 1-5 person team should avoid generic AI wrappers and instead target narrow, repeated, high-cost workflows where buyers already spend money. The practical opportunity is not "AI feature first"; it is "service-led workflow capture, then software sedimentation." This maps directly to `openSource_scanner`: the scanner should look for repos that can become a vertical workflow product, implementation wedge, or concierge-plus-thin-software offer.

The mental model for future scans should be:

- Existing budget: the buyer already pays for software, services, headcount, compliance, portals, or manual operations.
- Dirty workflow: the process requires chasing people, collecting documents, checking versions, routing approvals, exporting files, or reconciling status.
- High error cost: mistakes cause lost deals, failed audits, expired licenses, chargeback losses, missed renewals, or margin erosion.
- Service-to-software path: the first sale can be a concierge pilot, while the reusable pieces later become software.

## What This Changes For The Scanner

The current vertical report already lowers generic framework weight. This memo narrows the target further: prioritize repos that express a payable workflow, not just a vertical noun.

High-priority workflow families:

1. RFP / Proposal / Security Questionnaire response
2. Agency / consulting / implementation client delivery OS
3. Multi-location license / permit / renewal / inspection tracking
4. Vendor compliance / COI / credential tracking
5. Accounting / bookkeeping / tax client portals and document chasing
6. Trust center lite / security review workflow
7. Chargeback / dispute evidence builders
8. Proposal-to-SOW-to-change-order workflow
9. Niche client portals for legal, immigration, loan, consulting, and advisory workflows
10. Credential / CE / renewal tracking for licensed workers
11. AP vendor onboarding, W-9, bank info, and 1099 workflow
12. Small-industry CRM + quote + follow-up
13. Franchise / small chain compliance portals
14. Construction permit / submittal / PDF workflow
15. Productized implementation services for one narrow vertical
16. Niche intelligence products where the value is expert filtering plus templates

Lower-priority families unless there is a very specific workflow wedge:

- Generic AI dashboards, chatbots, agents, note tools, and task panels
- Generic CRM, generic PM, generic workflow automation, generic BI, generic website/app builders
- Web frameworks, component libraries, templates, SDKs, examples, awesome lists, survey papers
- Broad seller tooling, broad sales tooling, and platform-dependent automation unless the risk is explicit and manageable

## Search Query Expansion

Add query packs around buyer workflow language rather than only repo category language.

RFP / proposal / security questionnaire:

- `rfp response management open source`
- `proposal management open source`
- `security questionnaire automation`
- `ddq response workflow`
- `trust center questionnaire`
- `answer library proposal`

Agency / consulting client delivery:

- `client portal agency open source`
- `customer portal approval workflow agency`
- `scope change request management`
- `sow proposal change order`
- `implementation client onboarding portal`
- `project approval client portal`

Permits, licenses, inspections:

- `permit renewal tracking`
- `license expiration tracking`
- `inspection management multi location`
- `franchise compliance portal`
- `restaurant permit tracking`
- `health inspection checklist`

Vendor compliance / COI / credentials:

- `certificate of insurance tracking`
- `vendor compliance management`
- `contractor credential tracking`
- `vendor onboarding w9`
- `supplier document collection`
- `license verification renewal`

Finance / documents / disputes:

- `chargeback evidence builder`
- `dispute management evidence`
- `invoice quote pdf generator`
- `tax client portal document checklist`
- `bookkeeping client portal`
- `1099 vendor onboarding`

Industry workflow wedges:

- `construction submittal workflow`
- `construction permit tracker`
- `loan officer client portal`
- `immigration consultant client portal`
- `legal client document portal`
- `home health credential tracking`
- `dental license renewal tracking`

## Scoring Implications

Boost when a repo includes:

- Explicit buyer roles: proposal manager, agency, consultant, AP team, compliance manager, property manager, restaurant operator, franchise operator, bookkeeper, tax firm, permit expediter.
- Workflow verbs: approve, review, renew, expire, chase, collect, onboard, submit, export, evidence, dispute, credential, inspection, signoff, change order.
- Responsibility and audit language: owner, audit log, approval history, evidence, source-linked, compliance, checklist, renewal, expiration, exception.
- Export and document formats: Word, Excel, PDF, DOCX, XLSX, form package, evidence packet, signed document.
- Pricing-friendly unit economics: per vendor, per location, per permit, per client, per project, per active customer, per employee credential.
- Concierge-MVP potential: import spreadsheet, document checklist, manual review queue, status portal, alerts, templates.

Downrank when a repo is:

- A library, SDK, API wrapper, component set, template, awesome list, paper collection, demo, starter, boilerplate, or generic framework.
- A generic AI agent, generic notes app, generic chat UI, generic task board, or generic workflow runner.
- Platform automation with high ToS or account risk, unless the workflow is framed as compliant reporting, evidence, or human-reviewed operations.
- A broad horizontal product with no specific buyer, no operational responsibility, and no clear "who pays now" signal.

## Recommended Next Project Changes

1. Add a workflow-family taxonomy separate from the current broad category and vertical category.
2. Add report flags:
   - `--focus workflow`
   - `--workflow-family rfp,agency,permits,vendor-compliance,client-portal`
   - `--min-workflow-score`
3. Add score reasons so reports explain why a repo is surfaced, for example `workflow signal: renewal + expiration + location`.
4. Add a risk layer for platform automation, sensitive compliance claims, unknown licenses, demo repos, and libraries-only repos.
5. Add a memo template for "service-led validation" with:
   - buyer
   - current workaround
   - concierge pilot offer
   - reusable software module
   - first 20 outbound targets
   - pricing test
   - disqualifying risks

## Priority For The Next Scans

Run scans in this order:

1. RFP / proposal / security questionnaire response
2. Agency / consulting client delivery and change-order workflows
3. Permit / license / inspection renewal tracking for multi-location operators
4. Vendor compliance, COI, credential, and W-9 onboarding
5. Accounting / bookkeeping / tax client portals
6. Chargeback / dispute evidence builders
7. Construction permit and submittal workflows
8. Niche professional-service client portals

The scanner should treat these as "opportunity theses", not just keywords. A repo is interesting when it can plausibly support a paid pilot in 2-4 weeks.

## Immediate Shortlist Hypothesis

From the existing database and recent vertical reports, the candidates most aligned with this memo are likely:

- `open-condo-software/condo` - property workflow, tickets, residents, payments, invoices
- `microrealestate/microrealestate` - landlord/rental management
- `bigprof-software/online-rental-property-manager` - rental properties, tenants, leases
- `ChurchCRM/CRM` - membership and community operations
- `TDuckCloud/tduck-survey-form` - forms and questionnaires, but needs buyer-specific packaging
- `jfqd/redmine_helpdesk` - support workflow plugin, potentially niche service desk packaging
- `billabear/billabear` - subscription billing workflow
- `angelodlfrtr/go-invoice-generator` - document generation component, best as a building block rather than standalone SaaS
- `yuriycto/AcumaticaInventoryScanner` - inventory workflow with barcode and live stock lookup
- `georgewangchn/VetVoice` - veterinary clinic workflow with clear vertical specificity

None of these should be accepted solely by repo score. Each needs a memo against the report's three filters: existing budget, dirty workflow, high error cost.

## Decision

Use the report as a strategic filter for future exploration. The scanner should evolve from "find promising open-source projects" toward "find open-source building blocks or under-packaged products that can support a service-led workflow business."

