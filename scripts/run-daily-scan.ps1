Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path -Path $PSScriptRoot -ChildPath '..')).Path

Push-Location -LiteralPath $RepoRoot
try {
    uv run oss-scan scan --limit 50
    uv run oss-scan report --today
}
finally {
    Pop-Location
}
