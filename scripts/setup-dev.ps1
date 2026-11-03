<#
.SYNOPSIS
  Sets up a native-Windows Odoo 18 development environment for Kitaab (ADR-0003).

.DESCRIPTION
  1. Fetches every repo in repos.json at its pinned commit into vendor/<name> (shallow, gitignored).
  2. Creates .venv with the Python version from repos.json via uv and installs Odoo's requirements.
     uv is used because Odoo 18 needs Python 3.10-3.12 and the system Python may be newer.
  3. Writes odoo.conf (gitignored) with the addons path, unless it already exists.
  Safe to rerun: repos already at the pinned commit are left alone.

.PARAMETER CreateDbRole
  Also create the local PostgreSQL role Odoo connects as. psql prompts for the postgres superuser
  password.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\setup-dev.ps1
  .venv\Scripts\python vendor\odoo\odoo-bin -c odoo.conf
#>
param([switch]$CreateDbRole, [switch]$SkipPython)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$manifest = Get-Content (Join-Path $root 'repos.json') -Raw | ConvertFrom-Json
$vendor = Join-Path $root 'vendor'
New-Item -ItemType Directory -Force $vendor | Out-Null

foreach ($repo in $manifest.repos) {
    $dir = Join-Path $vendor $repo.name
    if (-not (Test-Path (Join-Path $dir '.git'))) {
        git init -q $dir
        git -C $dir remote add origin $repo.url
    }
    $head = git -C $dir rev-parse -q --verify HEAD 2>$null
    if ($head -eq $repo.commit) {
        Write-Host "same    $($repo.name) @ $($repo.commit.Substring(0,10))"
        continue
    }
    # Fetching the exact commit (not the branch tip) keeps every machine on identical upstream code.
    git -C $dir fetch -q --depth 1 origin $repo.commit
    if ($LASTEXITCODE -ne 0) { throw "fetch failed for $($repo.name)" }
    git -C $dir -c advice.detachedHead=false checkout -q FETCH_HEAD
    Write-Host "fetched $($repo.name) @ $($repo.commit.Substring(0,10))"
}

$venvPython = Join-Path $root '.venv\Scripts\python.exe'
if (-not $SkipPython) {
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        throw 'uv not found. Install it with: winget install astral-sh.uv'
    }
    if (-not (Test-Path $venvPython)) {
        uv venv --python $manifest.python (Join-Path $root '.venv')
    }
    uv pip install --python $venvPython -r (Join-Path $vendor 'odoo\requirements.txt')
    if ($LASTEXITCODE -ne 0) { throw 'installing Odoo requirements failed' }
    uv pip install --python $venvPython @($manifest.extraPythonPackages)
    if ($LASTEXITCODE -ne 0) { throw 'installing extra Python packages failed' }
}

$conf = Join-Path $root 'odoo.conf'
if (-not (Test-Path $conf)) {
    $paths = @()
    foreach ($repo in $manifest.repos) {
        foreach ($p in $repo.addonsPaths) {
            $paths += (Resolve-Path (Join-Path (Join-Path $vendor $repo.name) $p)).Path
        }
    }
    # Kitaab's own modules live in addons/ and join the path once the first one exists.
    $own = Join-Path $root 'addons'
    if (Test-Path $own) { $paths += $own }
    $dbPassword = $env:KITAAB_DB_PASSWORD
    if (-not $dbPassword) { $dbPassword = 'odoo' }
    $lines = @(
        '[options]',
        "addons_path = $($paths -join ',')",
        "data_dir = $(Join-Path $root '.odoo-data')",
        'db_host = localhost',
        'db_port = 5432',
        'db_user = odoo',
        "db_password = $dbPassword",
        'http_port = 8069',
        # ADR-0005: Odoo's daily usage report is pointed at a dead local port, so it cannot reach
        # Odoo S.A. even before kitaab_privacy is installed.
        'publisher_warranty_url = http://127.0.0.1:9/',
        # Hosts kitaab_privacy's egress guard lets the server reach (comma-separated); empty = none.
        'kitaab_egress_allowlist = '
    )
    Set-Content -Path $conf -Value $lines -Encoding ascii
    Write-Host "wrote   odoo.conf"
} else {
    Write-Host "kept    odoo.conf (delete it to regenerate the addons path)"
}

if ($CreateDbRole) {
    $pg = Get-ChildItem 'C:\Program Files\PostgreSQL' -Directory | Sort-Object { [int]$_.Name } | Select-Object -Last 1
    if (-not $pg) { throw 'PostgreSQL not found under C:\Program Files\PostgreSQL. Install it with: winget install PostgreSQL.PostgreSQL.16' }
    $dbPassword = $env:KITAAB_DB_PASSWORD
    if (-not $dbPassword) { $dbPassword = 'odoo' }
    & (Join-Path $pg.FullName 'bin\psql.exe') -U postgres -h localhost -c "CREATE ROLE odoo LOGIN CREATEDB PASSWORD '$dbPassword';"
}
