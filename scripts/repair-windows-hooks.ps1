# Repair Aftertone on Windows: global hooks, v2 defaults, daemon.
#   powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\aftertone\scripts\repair-windows-hooks.ps1"

$ErrorActionPreference = "Stop"
$env:Path = "$env:USERPROFILE\.local\bin;C:\Program Files\Git\cmd;C:\Program Files\Git\bin;$env:Path"

$Install = if ($env:AFTERTONE_INSTALL_DIR) { $env:AFTERTONE_INSTALL_DIR } else { Join-Path $env:USERPROFILE "aftertone" }
if (-not (Test-Path (Join-Path $Install "py\speak_summary_prepare.py"))) {
    Write-Error "Aftertone not found at $Install. Run: irm https://raw.githubusercontent.com/omarelkhal/aftertone/main/scripts/install.ps1 | iex"
}

$here = (Get-Location).Path
$projHook = Join-Path $here ".cursor\hooks.json"
if (Test-Path $projHook) {
    Remove-Item $projHook -Force
    Write-Host "Removed project hooks.json at $projHook (use global hooks only)"
}

Push-Location (Join-Path $Install "py")
& uv run python -m aftertone repair
$rc = $LASTEXITCODE
Pop-Location
if ($rc -ne 0) { exit $rc }

Write-Host ""
Write-Host "Aftertone v2 repair done. Reload Cursor, then run /aftertone-doctor or:"
Write-Host "  uv run --directory $Install\py python -m aftertone doctor"
