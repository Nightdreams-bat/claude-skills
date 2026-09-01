# Copy skills into your Claude Code skills directory. Existing skills are kept
# unless you pass -Force.
param([switch]$Force)
$ErrorActionPreference = 'Stop'
$dest = if ($env:CLAUDE_CONFIG_DIR) { Join-Path $env:CLAUDE_CONFIG_DIR 'skills' } else { Join-Path $env:USERPROFILE '.claude\skills' }
$src  = Join-Path $PSScriptRoot 'skills'
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Get-ChildItem -Directory $src | ForEach-Object {
    $target = Join-Path $dest $_.Name
    if ((Test-Path $target) -and -not $Force) { Write-Host "skip       $($_.Name) (already installed; -Force to overwrite)"; return }
    if (Test-Path $target) { Remove-Item -Recurse -Force $target }
    Copy-Item -Recurse $_.FullName $target
    Write-Host "installed  $($_.Name)"
}
Write-Host ""; Write-Host "Done. Restart Claude Code."
