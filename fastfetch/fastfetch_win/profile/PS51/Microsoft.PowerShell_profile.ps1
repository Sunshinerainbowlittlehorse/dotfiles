# Windows PowerShell 5.1 profile —— 加载与 PowerShell 7 共用的启动脚本
# 逻辑/开关都在 Documents\PowerShell\Fastfetch.ps1
$__startup = Join-Path $env:USERPROFILE 'Documents\PowerShell\Fastfetch.ps1'
if (Test-Path -LiteralPath $__startup) { . $__startup }
Remove-Variable -Name __startup -ErrorAction SilentlyContinue
