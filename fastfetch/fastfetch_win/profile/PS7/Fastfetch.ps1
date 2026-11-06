# ╔══════════════════════════════════════════════════════════════════╗
#  PowerShell 启动美化：UTF-8 + fastfetch（Catppuccin Mocha 预设）
#  由 pwsh 7 和 Windows PowerShell 5.1 的 profile 共同引用，别直接改
#  这里，改 fastfetch 外观请用： ffedit
#
#  开关（环境变量）：
#    FASTFETCH_AUTO=0   永久/临时关掉开机自动跑 fetch
#    FASTFETCH_AUTO=1   强制跑（即使输出被重定向，方便截图/测试）
#    PS_CLEAR=0         不清屏
# ╚══════════════════════════════════════════════════════════════════╝

$script:FastfetchConfig = Join-Path $env:USERPROFILE '.config\fastfetch\config.jsonc'

# usagebar 渐变条函数库（点源只定义 Update-UsageBarCache；缓存由本进程刷新，fastfetch 只读文件）
$script:UsageBarPs1 = Join-Path (Split-Path -Parent $script:FastfetchConfig) 'usagebar.ps1'
if (Test-Path -LiteralPath $script:UsageBarPs1) { . $script:UsageBarPs1 }

function Get-FastfetchPath {
    $cmd = Get-Command fastfetch.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $guess = Join-Path $env:LOCALAPPDATA 'Programs\fastfetch\fastfetch.exe'
    if (Test-Path $guess) { return $guess }
    $cmd = Get-Command fastfetch -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    return $null
}

function Invoke-Fastfetch {
    <#
        手动跑一次 fetch： ff / ff -Config <path> / ff --logo none / ff --pipe false
        多余参数原样透传给 fastfetch。
    #>
    [CmdletBinding()]
    param(
        # 命名参数：-Config / -c；不要写成位置参数，否则 ff --logo none 里的
        # '--logo' 会被吞进 -Config
        [Alias('Configpath', 'c')]
        [string]$Config,
        [Parameter(Position = 0, ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )

    # 宽容写法：ff <某个存在的预设文件>  -> 自动当 -Config 用
    if (-not $Config -and $Arguments) {
        $first = $Arguments[0]
        if ($first -and -not $first.StartsWith('-') -and (Test-Path -LiteralPath $first -ErrorAction SilentlyContinue)) {
            $Config = $first
            $Arguments = @($Arguments | Select-Object -Skip 1)
            if (-not $Arguments) { $Arguments = $null }
        }
    }

    $exe = Get-FastfetchPath
    if (-not $exe) {
        Write-Warning 'fastfetch.exe 未找到（检查 %LOCALAPPDATA%\Programs\fastfetch 是否在 PATH）'
        return
    }
    if (-not $Config) { $Config = $script:FastfetchConfig }
    if (Get-Command Update-UsageBarCache -ErrorAction SilentlyContinue) {
        try { Update-UsageBarCache } catch { }
    }


    # fastfetch 输出 UTF-8：只在跑它的这几帧里切代码页，结束后还原，
    # 避免影响依赖 GBK(936) 的老程序输出。
    $prev = $null
    try { $prev = [Console]::OutputEncoding } catch {}
    try {
        try { [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false) } catch {}
        if ($Config -and (Test-Path -LiteralPath $Config)) {
            & $exe '--config' $Config @Arguments
        }
        else {
            & $exe @Arguments
        }
    }
    finally {
        if ($prev) { try { [Console]::OutputEncoding = $prev } catch {} }
    }
}

function Edit-FastfetchConfig {
    <# 用记事本打开 fastfetch 预设（config.jsonc / logo） #>
    param([ValidateSet('config', 'logo', 'dir')][string]$What = 'config')
    $dir = Split-Path -Parent $script:FastfetchConfig
    $target = switch ($What) {
        'config' { $script:FastfetchConfig }
        'logo'   { Join-Path $dir 'ascii.txt' }
        'dir'    { $dir }
    }
    if (Test-Path -LiteralPath $target) { Invoke-Item -LiteralPath $target }
    else { Write-Warning "找不到 $target" }
}

function Set-FastfetchLogo {
    <#
        浏览 / 预览 / 固定 fastfetch 的 ascii 图案。
          fflogo                      列出可用图案（~\.config\fastfetch\logos 及上级目录）
          fflogo LierB-cat            临时预览，不动配置
          fflogo LierB-cat -Save      写进 config.jsonc（下次启动就是它）
          fflogo 某图 -Big            预览时用上下排版（高/宽图案不挤压信息区）
          fflogo -Reset               还原成默认（作者的猫 ascii.txt）
    #>
    [CmdletBinding()]
    param(
        [Parameter(Position = 0)][string]$Name,
        [switch]$Save,
        [switch]$Reset,
        [switch]$Big
    )

    $cfgDir   = Split-Path -Parent $script:FastfetchConfig
    $cfg      = $script:FastfetchConfig
    $default  = Join-Path $cfgDir 'ascii.txt'

    function Write-LogoSource([string]$Path) {
        # 只改 logo.source 那一行；用正斜杠，fastfetch 两边都吃
        $fixed = $Path.Replace([string][char]92, '/')
        # 换 PC 也能用：家目录前缀统一写成 %USERPROFILE%
        $homeFs = $env:USERPROFILE.Replace([string][char]92, '/')
        if ($fixed.StartsWith($homeFs)) { $fixed = '%USERPROFILE%' + $fixed.Substring($homeFs.Length) }
        $raw = Get-Content -LiteralPath $cfg -Raw -Encoding UTF8
        $m = [regex]::Match($raw, '"source"([^"]*)"([^"]*)"')
        if (-not $m.Success) { Write-Warning 'config.jsonc 里没找到 "source"，未修改'; return $false }
        if ($m.Groups[2].Value -eq $fixed) { return $true }          # 已经指向它了
        $built = '"source"' + $m.Groups[1].Value + '"' + $fixed + '"'
        $new = $raw.Remove($m.Index, $m.Length).Insert($m.Index, $built)
        [System.IO.File]::WriteAllText($cfg, $new, [System.Text.UTF8Encoding]::new($false))
    }

    if ($Reset) {
        if (Write-LogoSource $default) { Write-Host "已还原：$default" -ForegroundColor Green; Invoke-Fastfetch }
        return
    }

    # 收集候选：logos\ 子目录 + 配置目录下的 ascii*.txt
    $pool = @()
    $sub  = Join-Path $cfgDir 'logos'
    if (Test-Path $sub) { $pool += Get-ChildItem -LiteralPath $sub -File | Sort-Object Name }
    $pool += Get-ChildItem -LiteralPath $cfgDir -File -Filter 'ascii*.txt' | Where-Object Name -ne 'ascii.txt' | Sort-Object Name
    if (Test-Path $default) { $pool = @((Get-Item -LiteralPath $default)) + $pool }

    if (-not $Name) {
        $cur = ((Select-String -LiteralPath $cfg -Pattern '"source"\s*:\s*"([^"]*)"' -Encoding UTF8).Matches[0].Groups[1].Value)
        Write-Host "当前 logo: $cur" -ForegroundColor Cyan
        Write-Host "可用图案（fflogo <名字> 预览，加 -Save 固定）：" -ForegroundColor Gray
        foreach ($f in $pool) {
            $mark = if ($cur -and ($cur -like ('*' + (Split-Path $f.Name -Leaf)))) { '*' } else { ' ' }
            $lines = (Get-Content -LiteralPath $f.FullName -Encoding UTF8 | Where-Object { $_.Trim() }).Count
            Write-Host ("  {0} {1,-22} {2,3} 行  {3}" -f $mark, $f.BaseName, $lines, $f.Directory.Name)
        }
        return
    }

    $hit = $pool | Where-Object { $_.BaseName -ieq $Name -or $_.Name -ieq $Name -or $_.BaseName -ieq ($Name -replace '\.txt$','') } | Select-Object -First 1
    if (-not $hit) {
        Write-Warning ("找不到图案 '$Name'，先敲 fflogo 看列表")
        return
    }

    if ($Save) {
        if (Write-LogoSource $hit.FullName) { Write-Host "已固定 logo -> $($hit.Name)" -ForegroundColor Green }
        Invoke-Fastfetch
    }
    else {
        $extra = @('--file', $hit.FullName)
        if ($Big) { $extra += @('--logo-position', 'top') }
        Invoke-Fastfetch -Arguments $extra
    }
}

Set-Alias -Name ff     -Value Invoke-Fastfetch     -ErrorAction SilentlyContinue
Set-Alias -Name fflogo -Value Set-FastfetchLogo  -ErrorAction SilentlyContinue
Set-Alias -Name ffedit -Value Edit-FastfetchConfig -ErrorAction SilentlyContinue

# ── 自动运行：只在真正的交互式终端里，避免污染脚本 / CI / Agent 的输出 ──
$isConsoleHost = $Host.Name -eq 'ConsoleHost'
$isInteractive = -not [Console]::IsOutputRedirected -and -not [Console]::IsInputRedirected
$forced  = $env:FASTFETCH_AUTO -eq '1'
$disabled = $env:FASTFETCH_AUTO -eq '0'

if (-not $disabled -and (Get-FastfetchPath) -and ($forced -or ($isConsoleHost -and $isInteractive))) {
    # 清屏只在对屏幕说话时做：输出被重定向时 Clear-Host 会抛「句柄无效」
    if ($env:PS_CLEAR -ne '0' -and $isInteractive) {
        try { Clear-Host } catch { }
    }
    Invoke-Fastfetch
}
