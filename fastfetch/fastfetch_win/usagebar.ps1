# usagebar: RAM/Disk 16 格逐格真彩渐变条（fastfetch command 模块的数据源）
#
# 两种用法：
#   1) 被 Documents\PowerShell\Fastfetch.ps1 点源 -> 只定义 Update-UsageBarCache，
#      每次开窗 / ff 时在【当前 shell 进程内】刷新缓存（不额外孵 pwsh）
#   2) pwsh -NoProfile -File usagebar.ps1 -Run -> 手动刷新并打印（测试用）
#
# fastfetch 侧只做：cmd /c type usagebar.cache.txt（~40ms，不跑 PowerShell）
# 旋钮都在 Update-UsageBarCache 顶部：BAR_W / 两条渐变 / 阈值 / CACHE_TTL
param([switch]$Run)

function Update-UsageBarCache {
    $ErrorActionPreference = 'Stop'
    $e     = [char]27
    $BLK   = [char]0x2588
    $TRK   = [char]0x2591
    $RESET = "$e[0m"
    $BAR_W = 16
    $CACHE_TTL = 30          # 秒；缓存新鲜期内开窗零计算。0 = 每次都算

    # ---- 配色（Catppuccin Mocha）----
    $KEYC   = @(137,180,250)   # 键名（Hardware 蓝）
    $TXTC   = @(205,214,244)   # 正文
    $WARN   = @(249,226,175)
    $DANGER = @(243,139,168)
    $RAMP_RAM = @(@(137,180,250), @(180,190,254), @(203,166,247), @(245,194,231))  # 蓝->薰衣草->紫->粉
    $RAMP_DSK = @(@(148,226,213), @(166,227,161))                                  # 青->绿
    $SAFE_RAM = @(137,180,250); $SAFE_DSK = @(148,226,213)
    $RAM_WARN = 60; $RAM_DANG = 85
    $DSK_WARN = 70; $DSK_DANG = 90

    $dir    = $PSScriptRoot
    $txtF   = Join-Path $dir 'usagebar.cache.txt'
    $tsF    = Join-Path $dir 'usagebar.cache.ts'

    # TTL 内直接复用（开窗最快路径）
    if ($CACHE_TTL -gt 0 -and (Test-Path -LiteralPath $tsF) -and (Test-Path -LiteralPath $txtF)) {
        try {
            $age = ([DateTime]::UtcNow.Ticks - [long](Get-Content -LiteralPath $tsF -Raw)) / 1e7
            if ($age -le $CACHE_TTL) { return }
        } catch { }
    }

    function Fg($c) { "$e[38;2;$($c[0]);$($c[1]);$($c[2])m" }
    function Blend($a, $b, [double]$t) {
        @([int]($a[0] + ($b[0]-$a[0])*$t), [int]($a[1] + ($b[1]-$a[1])*$t), [int]($a[2] + ($b[2]-$a[2])*$t))
    }
    function Dim($c, [double]$k) { @([int]($c[0]*$k), [int]($c[1]*$k), [int]($c[2]*$k)) }
    function Ramp($stops, [double]$t) {
        if ($t -le 0) { return @($stops[0][0], $stops[0][1], $stops[0][2]) }
        if ($t -ge 1) { return @($stops[-1][0], $stops[-1][1], $stops[-1][2]) }
        $n = $stops.Count - 1; $x = $t * $n; $i = [int][math]::Floor($x)
        if ($i -ge $n) { $i = $n - 1 }
        Blend $stops[$i] $stops[$i+1] ($x - $i)
    }
    function StateColor([double]$p, [double]$w, [double]$d, $safe) {
        if ($p -ge $d) { $DANGER } elseif ($p -ge $w) { $WARN } else { $safe }
    }
    function Bar([double]$p, $ramp, [double]$wt, [double]$dt) {
        $fill = [int][math]::Floor($p / 100.0 * $BAR_W + 0.5)
        if ($fill -eq 0 -and $p -gt 0) { $fill = 1 }
        if ($fill -gt $BAR_W) { $fill = $BAR_W }
        $sb = New-Object System.Text.StringBuilder
        for ($i = 0; $i -lt $BAR_W; $i++) {
            $base = Ramp $ramp ($i / ($BAR_W - 1))
            $cellPct = ($i + 1) / $BAR_W * 100.0
            if ($i -lt $fill) {
                $c = $base
                if ($cellPct -gt $dt)     { $c = Blend $base $DANGER 0.55 }
                elseif ($cellPct -gt $wt) { $c = Blend $base $WARN 0.45 }
                if ($i -eq $fill - 1) {
                    if ($p -ge $dt)     { $c = $DANGER }
                    elseif ($p -ge $wt) { $c = $WARN }
                    else { $c = @([math]::Min(255,[int]($c[0]*1.15)), [math]::Min(255,[int]($c[1]*1.15)), [math]::Min(255,[int]($c[2]*1.15))) }
                }
                [void]$sb.Append((Fg $c)); [void]$sb.Append($BLK)
            } else {
                $c = Dim $base 0.28
                if ($cellPct -gt $dt)     { $c = Blend $c (Dim $DANGER 0.85) 0.40 }
                elseif ($cellPct -gt $wt) { $c = Blend $c (Dim $WARN 0.85) 0.30 }
                [void]$sb.Append((Fg $c)); [void]$sb.Append($TRK)
            }
        }
        [void]$sb.Append($RESET)
        $sb.ToString()
    }
    function FmtSize([double]$b) {
        $u = @('B','KB','MB','GB','TB','PB'); $i = 0; $v = $b
        while ($v -ge 1024 -and $i -lt 5) { $v /= 1024; $i++ }
        if ($i -le 1) { return ('{0:F0} {1}' -f $v, $u[$i]) }
        return ('{0:F1} {1}' -f $v, $u[$i])
    }
    function Row($icon, [string]$label, [double]$used, [double]$tot, [double]$p, $ramp, [double]$wt, [double]$dt, $safe) {
        $lab = $label.PadRight(10)
        $st  = StateColor $p $wt $dt $safe
        (Fg $KEYC) + $icon + ' ' + $lab + $RESET + ' ' + (Bar $p $ramp $wt $dt) + (Fg $TXTC) + (' {0} / {1} ' -f (FmtSize $used), (FmtSize $tot)) + (Fg $st) + ('({0}%)' -f $p) + $RESET
    }

    Add-Type -AssemblyName Microsoft.VisualBasic
    $ci = New-Object Microsoft.VisualBasic.Devices.ComputerInfo
    $t = [double]$ci.TotalPhysicalMemory
    $u = [double]($t - $ci.AvailablePhysicalMemory)
    $lines = @(Row ([char]0xEFC5) 'RAM' $u $t ([int][math]::Floor($u/$t*100+0.5)) $RAMP_RAM $RAM_WARN $RAM_DANG $SAFE_RAM)

    $diskRows = [System.IO.DriveInfo]::GetDrives() |
        Where-Object { $_.DriveType -eq [System.IO.DriveType]::Fixed -and $_.IsReady } |
        Sort-Object Name |
        ForEach-Object {
            $t2 = [double]$_.TotalSize
            $u2 = [double]($_.TotalSize - $_.AvailableFreeSpace)
            $id = $_.Name.TrimEnd('\')
            Row ([char]0xF0A0) ("Disk ($id\)") $u2 $t2 ([int][math]::Floor($u2/$t2*100+0.5)) $RAMP_DSK $DSK_WARN $DSK_DANG $SAFE_DSK
        }
    $lines = @($lines) + @($diskRows)

    [System.IO.File]::WriteAllText($txtF, ($lines -join "`n"))
    [System.IO.File]::WriteAllText($tsF, [string][DateTime]::UtcNow.Ticks)
}

if ($Run) {
    Update-UsageBarCache
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    [Console]::Out.Write([System.IO.File]::ReadAllText((Join-Path $PSScriptRoot 'usagebar.cache.txt')))
}
