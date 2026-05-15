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

## Local setup

```powershell
uv sync
$env:GITHUB_TOKEN="your_token"
uv run oss-scan scan --limit 50
uv run oss-scan report --today
```

`GITHUB_TOKEN` is optional for small manual runs, but recommended to avoid low
unauthenticated API rate limits.

## Commands

```powershell
uv run oss-scan scan --limit 50
uv run oss-scan report --today
uv run oss-scan feedback github 123 package
```

Use the `Feedback target` shown in a report as the `source` and `source_id`
arguments for `feedback`.

Feedback statuses:

- `new`: default state
- `saved`: interesting but not urgent
- `dismissed`: hide from ranked reports
- `watch`: keep tracking
- `package`: create a deeper packaging memo
