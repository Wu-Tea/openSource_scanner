# Market Pain Radar Automation

## Status

Inactive historical workflow. The user deleted the standalone `market-pain-radar` automation on 2026-06-01. Do not recreate it until the Revenue Pipeline can produce judgment and execution outputs, not just market-pain records.

## Overview

When active, this automation would run roughly every three hours and write a local research record under `records/market-pain/`.

The goal is to discover market pain signals from public communities first, then search GitHub and adjacent open-source sources for tools that could help solve or prototype around those pains.

## Default Target

Prioritize solo-developer-friendly 2C and lightweight consumer opportunities:

- entertainment, games, toys, companions, creator tools, browser toys
- personal productivity and learning pain points when they can become small products
- social, content, fandom, focus, study, hobby, and creator workflows
- tools that can be prototyped or validated in 2-6 weeks

ERP and adjacent heavy enterprise operations software are banned from default records.

## Source Mix

Chinese communities:

- V2EX: 创意想法, 分享创造, 问与答, 程序员, 酷工作 only when it reveals pain, Apple, macOS, 生活, 游戏
- 少数派 / 即刻 / 小红书 / 知乎 / Bilibili when public search results expose useful pain signals

English communities:

- Hacker News: Ask HN, Show HN, Launch HN, relevant discussion threads
- Reddit: r/SomebodyMakeThis, r/SideProject, r/indiehackers, r/Entrepreneur, r/SaaS, r/gamedev, r/incremental_games, r/cozygamers, r/productivity, r/ADHD, r/languagelearning, r/learnprogramming, r/selfhosted only when consumer pain is clear
- Indie Hackers, Product Hunt, itch.io, Steam, Chrome Web Store, GitHub Trending/Search

## Run Rules

- This workspace runs on Windows. Local commands and examples should use PowerShell-compatible syntax. Avoid Unix-only heredocs such as `python <<'PY'`; prefer PowerShell here-strings like `@' ... '@ | uv run python -`, checked-in scripts, or native PowerShell commands.
- Use public pages, RSS feeds, official APIs, or normal search results where possible.
- Do not log in, bypass paywalls, scrape private data, collect personal identities, or store sensitive personal information.
- Keep request volume low. Prefer 5-10 high-signal pages per run over broad crawling.
- Cite source URLs for each pain signal.
- Exclude ERP, Odoo, SAP, accounting suites, invoicing systems, inventory/warehouse management, CRM, POS, Salesforce, NetSuite, and procurement by default.
- Downrank heavy B2B implementation, compliance, sales-led workflow, infrastructure, libraries-only repos, and generic AI wrappers.

## Output Path

Each run writes:

- `records/market-pain/YYYY-MM-DD-HHMM.md`

If useful, append one line to:

- `records/market-pain/index.md`

## Record Shape

Each record should include:

1. Run metadata: time, sources touched, safety notes.
2. Top pain signals: source, user language, pain summary, affected audience, urgency, evidence, quote or paraphrase.
3. Opportunity thesis: what could be built, why a solo developer can test it, expected prototype size.
4. GitHub/tool matches: repositories or tools that could help, with license/activity notes when available.
5. Rejected leads: why they were ignored, especially ERP/B2B/heavy implementation.
6. Next searches: targeted queries for the following run.

## Quality Bar

A good record should answer:

- What pain did real users express?
- Who has the pain?
- Why is the pain current or repeated?
- What small product angle could address it?
- What existing open-source tool or repo can accelerate a prototype?
- What should be ignored because it is too enterprise, too broad, too risky, or too large for one developer?
