# openSource_scanner

Open-source opportunity radar for finding projects that can be packaged into useful
products, services, templates, integrations, deployment kits, localization work, or
support offers.

Strategic note: as of 2026-05-20, the default product target is shifting toward
solo-developer-friendly 2C entertainment, companion, toy, and lightweight
consumer products. The existing GitHub/B2B/vertical workflow modes are still
useful as secondary lenses, but the next scanner iteration should prioritize
consumer-hit signals and non-GitHub sources such as Steam, itch.io, Product Hunt,
Reddit, and short-video/social communities. ERP-related applications are excluded
from default scans.

## First workflow

1. Scan GitHub for candidate repositories.
2. Normalize public metadata into opportunity records.
3. Score each record with explainable packaging and monetization signals.
4. Store history and feedback in SQLite.
5. Generate a Markdown report under `reports/`.
6. Generate a human review memo under `memos/` for candidates worth packaging.

## Local setup

```powershell
uv sync
$env:GITHUB_TOKEN="your_token"
uv run oss-scan scan --limit 50
uv run oss-scan report --today
```

`GITHUB_TOKEN` is optional for small manual runs, but recommended to avoid low
unauthenticated API rate limits.

The default GitHub query set is intentionally diversified across developer
tools, self-hosted infrastructure, automation, DevOps, security, monitoring,
data, analytics, no-code, productivity, APIs, CLIs, and a capped AI query. This
keeps the radar from turning into only an AI-project leaderboard.

Reports are balanced by category by default. The report command first picks a
small number of top projects from each detected category, then fills any
remaining slots by global score. Use `--global` when you want a pure score-only
ranking, or tune the first pass with `--per-category`.

```powershell
uv run oss-scan report --today --limit 30
uv run oss-scan report --today --limit 30 --per-category 2
uv run oss-scan report --today --limit 30 --global
uv run oss-scan report --today --focus vertical --limit 50
```

Use `--focus vertical` when looking for small business workflows or industry
pain points. It boosts explicit domains such as restaurants, bookings, forms,
CRM, property management, clinics, education, finance, events, and helpdesk,
while downranking generic web frameworks and component libraries.

## Safety

The GitHub scan uses conservative request guards before larger runs. By default,
one scan run makes at most 10 GitHub repository search requests, waits 2 seconds
between search requests, and stops early when the reported remaining search
quota reaches 2. You can override the first two values for one run:

```powershell
uv run oss-scan scan --max-search-requests 5 --min-seconds-between-requests 1
```

The scanner does not retry GitHub rate-limit failures in a loop. If GitHub
returns an error, the command exits with failure and prints rate-limit context
when available. Put `GITHUB_TOKEN` in your shell, task, or GitHub Actions secret
environment; do not write token values into committed files.

## Scheduled runs

GitHub Actions runs the optional daily scan around 09:00 Asia/Hong_Kong
(`01:00 UTC`) using `.github/workflows/daily-scan.yml`. It can also be started
manually from the Actions tab because the workflow supports `workflow_dispatch`.

For a local Windows schedule, create a Windows Task Scheduler task that calls
`scripts/run-daily-scan.ps1` with PowerShell. If authenticated GitHub API access
is needed, set `GITHUB_TOKEN` in the user or task environment before the script
runs.

Scheduled runs write Markdown reports under `reports/`. The local SQLite history
database is stored at `data/scanner.sqlite`.

## Commands

```powershell
uv run oss-scan scan --limit 50
uv run oss-scan report --today
uv run oss-scan feedback github 123 package
uv run oss-scan memo github 123
uv run oss-scan shortlist
```

Use the `Feedback target` shown in a report as the `source` and `source_id`
arguments for `feedback` and `memo`. For example, if the report says
`Feedback target: github 123`, run `uv run oss-scan memo github 123` to create
an opportunity memo in `memos/`.

The memo command will not overwrite an existing same-day memo by default, so
manual edits are protected. If you intentionally want to regenerate the file,
run `uv run oss-scan memo github 123 --force`.

Memos are human review aids. They summarize public project facts and suggest
conservative packaging hypotheses, but they are not legal advice, business
guarantees, or proof that a project can be commercialized safely.

The shortlist command turns feedback decisions into a lightweight pipeline
report at `reports/shortlist.md`. By default, it includes `package`, `watch`,
and `saved` opportunities so you can see what is ready for a memo or 7-day
experiment, what should be monitored, and what still needs a decision.

Feedback statuses:

- `new`: default state
- `saved`: interesting but not urgent
- `dismissed`: hide from ranked reports
- `watch`: keep tracking
- `package`: create a deeper packaging memo
