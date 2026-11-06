# PowerShell 7 profile —— 只做一件事：加载共用启动脚本
# 逻辑/开关都在 Documents\PowerShell\Fastfetch.ps1，Windows PowerShell 5.1 也用它
$__startup = Join-Path $env:USERPROFILE 'Documents\PowerShell\Fastfetch.ps1'
if (Test-Path -LiteralPath $__startup) { . $__startup }
Remove-Variable -Name __startup -ErrorAction SilentlyContinue
