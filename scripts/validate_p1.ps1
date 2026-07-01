param(
  [switch]$SkipFrontend
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

function Invoke-Checked {
  param(
    [Parameter(Mandatory = $true)]
    [ScriptBlock]$Command
  )
  & $Command
  if ($LASTEXITCODE -ne 0) {
    throw "Command failed with exit code $LASTEXITCODE"
  }
}

Set-Location $Root
Invoke-Checked { git diff --check }
Invoke-Checked { python -m compileall -q api agent parser scripts }
Invoke-Checked { python -m unittest discover -s tests -t . -p "test_*.py" -v }

if (-not $SkipFrontend) {
  Push-Location (Join-Path $Root "web")
  try {
    Invoke-Checked { npm run lint }
    Invoke-Checked { npm run build }
  }
  finally {
    Pop-Location
  }
}

Write-Host "P1 validation passed."
