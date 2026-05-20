# Fragmented Waiting Time Games Memo - 2026-05-20

Source report: `D:\Downloads\deep-research-report (12).md`

## Overview

This report studies a different opportunity track from the current B2B workflow scanner. It argues that AI-era work is creating more fragmented waiting states: delegate work to an agent, wait, review, approve, then redelegate. The opportunity is not a generic idle game and not an "AI game"; it is a desktop-first passive-active hybrid that lives at the edge of the screen while the user works.

The report's practical thesis is:

- AI-assisted work creates repeated short waiting windows.
- Short-form feeds already capture this attention, so the product must be lower-friction than social feeds and more meaningful than passive wallpaper.
- The best game shape is a desktop companion with passive progress plus 30-90 second bursts of meaningful decisions.
- This should be validated as a small experiment, not treated as a full-company direction until co-working retention is proven.

## External Checks

I spot-checked current public sources for the key market assumptions.

- OpenAI's current Codex docs say Codex cloud can work on tasks in the background and in parallel using its own cloud environment.
- OpenAI's Codex product page frames the app around multi-agent workflows, parallel work, and always-on background work.
- Steam's current page for `Rusty's Retirement` describes it as an idle farming simulator that sits at the bottom of the screen while users do other tasks; it has overwhelmingly positive review signals and a bottom-of-screen bundle.
- Steam's current page for `Ropuka's Idle Island` calls it a desktop sticker / co-working buddy and lists it in a bottom-of-screen bundle.
- Steam's current page for `Desktop Survivors 98` confirms that desktop-overlay action can work, but it is explicitly fast, bullet-hell, and reflex-heavy.

These checks support the report's core claim: the desktop companion micro-genre is real, and AI tooling is increasing background/parallel work rhythms. They do not prove mainstream demand for a new game; they justify a disciplined MVP test.

## Product Direction

The strongest direction is `Desktop Expedition Sticker RPG`.

One-line pitch:

> A bottom-of-screen settlement and expedition game where tiny workers progress while you work, then every few minutes you make a 30-90 second decision: route an expedition, resolve an event, equip a drop, choose a card, or challenge an elite node.

The key design promise:

- It is safe to ignore.
- It is rewarding to check.
- It never punishes sudden work resumption.
- It has more agency than cozy desktop wallpaper.
- It demands less attention than a survivor-like or deckbuilder.

## MVP Scope

Build one Windows-first prototype before considering Steam commitment.

Minimum feature set:

1. Bottom-bar desktop mode.
2. One settlement screen.
3. One expedition lane.
4. Four resources.
5. One hero or worker party.
6. One equipment slot.
7. One active event type.
8. One boss or elite encounter.
9. One prestige/reset hook.
10. Focus mode toggle.
11. Save/load that survives hard exits.

Avoid in the first MVP:

- Mobile.
- Multiplayer.
- Live-service systems.
- Long tactical runs.
- Punishing daily chores.
- Heavy daily caps.
- Fragile board states that are hard to resume.

## Design Rules

The game should be built around co-working retention, not raw playtime.

Core loop:

1. Passive workers generate resources while the user works.
2. The user checks back after a few minutes.
3. The game presents one clear decision.
4. The decision improves the next passive stretch.
5. The user can leave immediately without losing state.

Useful mechanics:

- Expedition routing.
- Event cards.
- One-click battle bursts.
- Item merge or equip choices.
- Short boss windows.
- Collection book.
- Automation unlocks.
- Prestige tree.
- Cosmetic settlement upgrades.

Design smells:

- The player feels they must babysit.
- The best play is to stare at the game.
- A check-in takes more than 90 seconds.
- The player forgets the game state after returning.
- The game is only decorative and has no meaningful decisions.

## Validation Metrics

The main metric is co-working retention.

Track:

- D1 return rate.
- D7 return rate.
- Average daily background-open minutes.
- Active interventions per hour of background time.
- Percentage of users who keep the game open during real work.
- Percentage of users who say it replaced at least some social-feed checking.
- Ratio of "left open while working" sessions to normal full-attention play sessions.

The MVP succeeds only if users naturally keep it open during work and return during wait states.

## Comparison With The Current Scanner Direction

This is not a replacement for the B2B workflow thesis.

The B2B workflow direction is stronger for near-term monetization because it has clearer existing budgets, business pain, and service-led validation paths. The desktop game direction is more speculative but potentially faster to prototype and easier to validate with a demo.

Recommended posture:

- Keep B2B workflow scanning as the mainline.
- Treat desktop waiting-time games as a side experiment.
- Do not let the scanner's B2B scoring be diluted by game-specific signals.
- If pursued, create a separate `game-opportunity` research track or a separate prototype repo.

## Build Path If We Pursue It

Thirty-day validation plan:

Week 1:

- Build the bottom-bar shell.
- Add passive resources.
- Add focus mode.
- Add one active event type.

Week 2:

- Add expedition gear.
- Add a boss or elite node.
- Add one prestige/reset mechanic.
- Add save/load and interruption-safe resume.

Week 3:

- Test with 20-30 AI-heavy workers, developers, solo builders, or knowledge workers.
- Instrument background-open time, check-in cadence, and intervention length.

Week 4:

- Cut a Steam-style demo page, short trailer, and GIF set.
- Test whether people understand the pitch in under 10 seconds.
- Decide whether to continue based on co-working retention, not enthusiasm alone.

## Risks

- This market is already being filled by bottom-of-screen cozy companions.
- The idea can fail by becoming too shallow, turning into wallpaper.
- It can also fail by becoming too active, turning into distraction.
- Steam review counts and public signals are proxies; wishlists and real sales are mostly private.
- The AI-wait behavior is strongest among heavy agent users and may not generalize.
- A game project can consume attention that may be better spent on the clearer B2B workflow opportunities.

## Decision

Record this as a worthwhile side experiment: "Desktop Expedition Sticker RPG / Passive-Active Hybrid Game." It is worth a 30-day prototype if we intentionally allocate a separate experiment lane. It should not interrupt the workflow-family scanner unless the user explicitly chooses to pursue a game prototype.

## 2026-05-20 Update

After user feedback, this direction should be reclassified. The user clarified that a solo developer is poorly matched to heavy B2B workflow opportunities and is better served by 2C entertainment or consumer small-hit products.

Under that updated strategy, `Desktop Expedition Sticker RPG` is no longer merely a side experiment. It becomes the first recommended validation lane for the new solo-developer 2C mainline. See `docs/research/2026-05-20-solo-dev-2c-entertainment-pivot.md` and `.agent-context/decisions/DEC-2026-05-20-001-solo-dev-2c-mainline.md`.
