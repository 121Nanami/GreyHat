$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
node tests/smoke.js
node --test (Get-ChildItem tests/*.test.js).FullName
Write-Host "smoke.ps1: all checks passed"
