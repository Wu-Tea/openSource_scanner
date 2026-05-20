# Solo Developer 2C Entertainment Pivot - 2026-05-20

## Overview

The scanner's original goal was broad: find open-source projects with packaging and monetization potential. Recent exploration drifted toward B2B workflows because the search sources and scoring signals favored GitHub repositories with deployment, workflow, compliance, dashboards, APIs, and existing business pain.

The user corrected the target on 2026-05-20: for a solo developer, many B2B workflow opportunities are too heavy. A better first target is a 2C entertainment or consumer micro-product that can become a small hit, especially if it can be built and validated quickly.

## What Changed

The primary discovery question should change from:

> What open-source business workflow can be packaged into a paid product or service?

to:

> What consumer-facing entertainment, companion, toy, or lightweight utility can a solo developer build, polish, distribute, and test for breakout potential?

This does not mean every opportunity must be a game. It means the scanner should prioritize:

- Emotional pull over operational budget.
- Shareability over enterprise pain.
- Fast prototype loops over complex sales.
- Solo-developer scope over service-heavy implementation.
- Audience resonance over feature completeness.

## Why The Previous Target Drifted

The earlier scanner was structurally biased:

- GitHub is mostly builders, not consumers.
- Stars reward developer interest more than consumer demand.
- Packaging keywords such as `deploy`, `hosted`, `workflow`, `dashboard`, `api`, and `integration` push results toward SaaS and B2B tooling.
- Vertical scoring rewarded business nouns such as invoice, booking, CRM, compliance, inventory, property, and clinic.
- Risk filters favored mature repositories with licenses and docs, which often means professional software rather than playful consumer products.

Those signals are useful for one kind of opportunity, but they are not the right center of gravity for a solo developer looking for a 2C small hit.

## New Mainline Direction

Treat 2C entertainment and consumer micro-products as the main discovery lane.

Best-fit opportunity families:

1. Desktop companions and bottom-of-screen games.
2. Cozy idle, incremental, collection, and passive-active games.
3. Tiny roguelite, survivor-like, puzzle, rhythm, typing, and one-mechanic games.
4. Browser toys, interactive widgets, generators, and meme tools.
5. Creator-facing playful tools: avatar makers, thumbnail toys, caption/image/video toys.
6. Socially shareable utilities: quizzes, personality tests, wrapped-style summaries, challenge generators.
7. Niche fandom tools and community toys, with IP/legal risk reviewed separately.
8. Low-production visual novels, horror shorts, dating sims, and narrative experiments.
9. Personalization products: desktop pets, focus buddies, ambient dashboards, status toys.
10. AI-assisted entertainment where AI reduces production cost, not where AI is the product pitch.

## Better Source Mix

GitHub should remain useful for engines, templates, codebases, mod tools, and buildable primitives, but it should no longer be the dominant truth source.

Higher-priority sources:

- Steam: New & Trending, Popular Upcoming, tags such as Cozy, Casual, Idler, Simulation, Puzzle, Visual Novel, Horror, Rhythm, Roguelite, Desktop, Clicker, Cute.
- itch.io: Top selling, New & Popular, browser games, game jam winners, horror, visual novel, simulation, puzzle, and $5-or-less paid experiments.
- Product Hunt: consumer apps, creator tools, AI toys, social widgets, browser extensions.
- Reddit: indie game, cozy game, incremental game, browser game, gamedev feedback, and niche fandom communities.
- TikTok / YouTube Shorts / Xiaohongshu: proof of visual hook and shareability.
- Chrome Web Store / Steam / App Store: distribution and review signals.
- GitHub: open-source implementation references and abandoned-but-buildable consumer ideas.

## Scoring Changes Needed

Add a consumer-hit score separate from current broad category and vertical scores.

Positive signals:

- `play in browser`, `demo`, `steam`, `itch`, `game jam`, `screenshots`, `gif`, `trailer`, `wishlist`, `reviews`, `ratings`.
- Genres with solo-dev feasibility: idle, incremental, cozy, puzzle, visual novel, horror short, rhythm, typing, desktop pet, avatar maker, generator.
- Clear 10-second visual hook.
- One-sentence pitch that non-technical users understand.
- Low content burden or procedural/UGC/content-loop support.
- Small install surface: web, Windows desktop, Steam demo, browser extension.
- Price-test friendly: free demo, $2-$10 paid, cosmetic/supporter DLC, asset pack, template, creator pack.

Negative signals:

- Enterprise, compliance, dashboard, devops, Kubernetes, observability, security platform.
- Multi-tenant SaaS, sales-led onboarding, procurement, long integration cycles.
- Heavy multiplayer, live ops, licensed IP dependency, large 3D content burden.
- Generic AI wrapper with no entertainment loop.
- Code-only libraries unless they are clearly useful for building a consumer toy quickly.

## Practical Product Thesis

The strongest current candidate remains the desktop waiting-time game, but it should be promoted from "side experiment" to the first 2C validation lane.

Best first prototype:

> Desktop Expedition Sticker RPG: a bottom-of-screen passive-active game for people working alongside AI agents, where tiny workers progress while the user works and the user makes short, meaningful decisions during wait states.

Why it fits the solo-developer target:

- Clear audience: AI-heavy workers, developers, students, and focus-tool users.
- Small scope: one desktop shell, one passive loop, one active event loop.
- Visual hook: bottom-of-screen workers moving while the user works.
- Distribution path: itch demo first, then Steam demo if retention looks promising.
- Monetization path: paid game, supporter pack, cosmetic pack, soundtrack, or later mobile/desktop variants.

## What The Scanner Should Do Next

1. Add a `consumer` or `2c` focus mode.
2. Add a consumer-hit taxonomy independent from B2B vertical taxonomy.
3. Add query packs for game, desktop companion, browser toy, generator, meme, avatar, focus buddy, and creator toy opportunities.
4. Add non-GitHub collectors or manual import support for Steam, itch.io, Product Hunt, Reddit, and Xiaohongshu findings.
5. Reduce default weight for B2B workflow terms unless the user explicitly selects a B2B focus.
6. Generate reports around "can a solo developer ship and test this in 2-6 weeks?"
7. Add memo templates that evaluate hook, audience, prototype scope, content burden, distribution path, and monetization test.

## Immediate Operating Rule

Until the scanner code is updated, treat B2B workflow results as secondary. The next scans should prefer 2C entertainment and consumer micro-product signals, even if GitHub stars are lower or the repository looks less mature.
