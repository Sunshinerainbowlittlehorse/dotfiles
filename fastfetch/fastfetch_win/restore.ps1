# fastfetch_win 一键还原（在任意 PowerShell 里执行本脚本）
$ErrorActionPreference = "Stop"
$src = $PSScriptRoot
$dst = Join-Path $env:USERPROFILE ".config\fastfetch"
New-Item -ItemType Directory -Force -Path $dst | Out-Null
foreach ($f in "config.jsonc","ascii.txt","ascii_flag.txt","usagebar.ps1","make_preset.py","import_neofetch.py","import_fetchsama.py","colorize.py","README.md") {
  if (Test-Path (Join-Path $src $f)) { Copy-Item (Join-Path $src $f) $dst -Force }
}
if (Test-Path (Join-Path $src "logos")) { Copy-Item (Join-Path $src "logos") $dst -Recurse -Force }
# PowerShell 胶水（pwsh 7 + Windows PowerShell 5.1）
Copy-Item (Join-Path $src "profile\PS7\Fastfetch.ps1") (Join-Path $env:USERPROFILE "Documents\PowerShell\Fastfetch.ps1") -Force
New-Item -ItemType Directory -Force -Path (Join-Path $env:USERPROFILE "Documents\PowerShell") | Out-Null
Copy-Item (Join-Path $src "profile\PS7\Fastfetch.ps1") (Join-Path $env:USERPROFILE "Documents\PowerShell\Fastfetch.ps1") -Force
Copy-Item (Join-Path $src "profile\PS7\Microsoft.PowerShell_profile.ps1") (Join-Path $env:USERPROFILE "Documents\PowerShell\Microsoft.PowerShell_profile.ps1") -Force
New-Item -ItemType Directory -Force -Path (Join-Path $env:USERPROFILE "Documents\WindowsPowerShell") | Out-Null
Copy-Item (Join-Path $src "profile\PS51\Microsoft.PowerShell_profile.ps1") (Join-Path $env:USERPROFILE "Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1") -Force
Write-Host "已还原。前提：fastfetch.exe 需在 %LOCALAPPDATA%\Programs\fastfetch 或 PATH 中。" -ForegroundColor Green
Write-Host "开新终端即生效。ExecutionPolicy 需 RemoteSigned（管理员： Set-ExecutionPolicy RemoteSigned -Scope LocalMachine -Force）。"
