# openSource_scanner

Open-source opportunity radar for finding projects that can be packaged into useful
products, services, templates, integrations, deployment kits, localization work, or
support offers.

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
```

Use the `Feedback target` shown in a report as the `source` and `source_id`
arguments for `feedback` and `memo`. For example, if the report says
`Feedback target: github 123`, run `uv run oss-scan memo github 123` to create
an opportunity memo in `memos/`.

Memos are human review aids. They summarize public project facts and suggest
conservative packaging hypotheses, but they are not legal advice, business
guarantees, or proof that a project can be commercialized safely.

Feedback statuses:

- `new`: default state
- `saved`: interesting but not urgent
- `dismissed`: hide from ranked reports
- `watch`: keep tracking
- `package`: create a deeper packaging memo
