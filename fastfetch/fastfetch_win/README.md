# fastfetch 美化预设（PowerShell 启动自动显示）

logo 用的是 **上游作者的原图**：https://github.com/SleepyCatHey/Ultimate-Win11-Setup
里 `Fastfetch/ascii.txt` 的那只 braille 猫，字节级照搬没改。
其余部分（模块、框线、路径、开关）是按本机情况重写的，比上游少踩几个坑。

## 文件

| 文件 | 作用 |
|---|---|
| `config.jsonc` | 预设本体（fastfetch 默认就读这个路径） |
| `ascii.txt` | **当前 logo：作者的 braille 猫**（`$1/$3/$4/$8` 是颜色占位符，由 `logo.color` 自动替换） |
| `ascii_flag.txt` | 备选：Windows 11 四色块旗（纯块元素，完全不依赖字体回退） |
| `ascii_cat.txt` | 备选：纯 ASCII 猫 |
| `make_preset.py` | 唯一生成器：改 `LW`/`INNER`/模块列表后 `python make_preset.py` 重新生成 `config.jsonc` + `ascii_flag.txt`（不碰作者的 `ascii.txt`） |
| 上游原文件缓存 | 想重新拉：`curl -o ascii.txt https://raw.githubusercontent.com/SleepyCatHey/Ultimate-Win11-Setup/main/Fastfetch/ascii.txt` |

## braille 猫是怎么在你现在这套字体下显示出来的

你 WT 的主字体是 `JetBrainsMono Nerd Font`，它**不含 braille 字形**（U+2800-U+28FF 覆盖 0/256）。
能显示是因为 Windows Terminal 对缺字做 DirectWrite 自动回退，而本机
`C:\Windows\Fonts\seguisym.ttf`（Segoe UI Symbol）braille 覆盖 **256/256**，正好补上。
上游作者的主字体也是 JBM Nerd Font，所以这条链路和他一致。

万一哪天猫变成方框/空心（换字体或换终端后），两条修法任选：

```powershell
# A. 给终端补一个含 braille 的回退字体（主字体视觉不变，Cascadia 随 WT 自带，无需安装）
#    改 settings.json -> profiles.defaults.font.face：
#    "JetBrainsMono Nerd Font, Cascadia Mono"
# B. 换不依赖回退的 logo：编辑 config.jsonc 把 logo.source 改成 ascii_flag.txt
```

## 启动链路

```
Documents\PowerShell\Microsoft.PowerShell_profile.ps1        <- pwsh 7
Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1 <- Windows PowerShell 5.1
        └── 都 dot-source Documents\PowerShell\Fastfetch.ps1
                ├── Invoke-Fastfetch     (别名 ff)     手动跑一次
                ├── Edit-FastfetchConfig (别名 ffedit) 打开 config.jsonc / logo
                └── 交互式终端时清屏 + 自动跑
```

`fastfetch.exe` 在 `%LOCALAPPDATA%\Programsastfetch`（2.71.0 便携版 zip，已写入用户 PATH；
profile 里还有绝对路径兜底，PATH 没刷新的窗口也能跑）。

## 开关（环境变量）

| 变量 | 效果 |
|---|---|
| `FASTFETCH_AUTO=0` | 不自动跑（`ff` 仍可用） |
| `FASTFETCH_AUTO=1` | 强制跑，即使输出被重定向（截图 / 远程调试） |
| `PS_CLEAR=0` | 启动不清屏 |

只有 `Host.Name -eq 'ConsoleHost'` 且 stdin/stdout 都没重定向时才自动执行，
所以脚本、CI、Agent 调 `pwsh -Command ...` 不会被污染输出。

## 去哪儿找更多 ascii 图案（都实测过链接可用）

### A. 不用下载：fastfetch 自带 545 个
```powershell
fastfetch --list-logos          # 全部名字（545 个发行版/品牌/彩蛋图案）
fastfetch --print-logos                 # 545 个内置图案挨个打印
ff -l arch --logo-type builtin -s os    # ⚠️ 试内置图案必须带上 --logo-type builtin
ff --file logos/LierB-rose -s os,cpu    # 试文件图案（--file 已隐含 type=file）
```
`-s`/`--structure` 临时挑模块（看小样很方便），`--logo-position top` 改上下排版。

⚠️ **坑**：`config.jsonc` 里 `logo.type` 是 `file`，所以命令行 `-l arch` 会被拿去当**文件名**找，
找不到就静默回落成系统默认图案（看着就像"换了个 logo 结果没变"）。
试内置图案要写全 `-l arch --logo-type builtin`；试文件用 `--file`（它等价于 `--logo-type file --logo <path>`）。
`ff` 函数已经把 `--file` 包好了，所以 `fflogo` 那条路没这个烦恼。内置的大多是发行版 logo，`AmogOS`、`GarudaDragon`、
`SteamDeck`、`GhostFreak` 这类彩蛋可以翻翻。

### B. GitHub 上的图案合集（我已下了一批到 `logos\`）

| 仓库 | 星 | 里面有什么 | 格式 |
|---|---|---|---|
| [LierB/fastfetch](https://github.com/LierB/fastfetch) | 446 | `ascii/`(cat/arch/rose/triangle) + `presets/` 8 套完整配置 + `images/` 图片 logo | .txt ✅ |
| [m3tozz/FastCat](https://github.com/m3tozz/FastCat) | 377 | 主题包：`Small-Themes`(21 个：Bunny/Cat/Coffee/Duck/Giraffe/OWL/Robo-Dog/Tie-Fighter/Wave…)、`Large-Themes`、`Visuals-Themes`，带 `start.sh` 安装器 | 目录（config+ascii） |
| [c-error/fetch-sama](https://github.com/c-error/fetch-sama) | – | `configs/*.txt` 动漫人物（neuro/anny/vedal/imp/aquwa/evil），**Windows 优先项目**（自带 build.bat），图案 39-45 行偏高 | .txt ✅ |
| [dlcgold/ascii-art-neofetch](https://github.com/dlcgold/ascii-art-neofetch) | 40 | 17 个 `.ascii`（Duck/Cake/Cube/Atom/Gurren_laggan/Nuclear…） | .ascii ✅（改不改扩展名都行） |
| [blyxyas/uwu-neofetch-art](https://github.com/blyxyas/uwu-neofetch-art) | 57 | `colored/` + `black-white/` 动漫系（doraemon/sailor-moon-cat/anime-eyes…），**braille 画的** | .txt ⚠️ 靠字体回退 |
| [SleepyCatHey/Ultimate-Win11-Setup](https://github.com/SleepyCatHey/Ultimate-Win11-Setup/tree/main/Fastfetch) | – | 你现在这只猫的出处 | .txt ⚠️ braille |

### C. 自己造
* **文字横幅**：[xero/figlet-fonts](https://github.com/xero/figlet-fonts)（1.6k★，1000+ figlet 字体）、
  [patorjk 的在线 figlet](http://patorjk.com/software/taag/) → 打出 ASCII 存成 txt 即可。
* **图片转 ASCII**：这个 build 编进了 `chafa`，`ff` 支持 `"logo": {"type":"chafa","source":"xx.png"}`；
  也可直接用图片：`logo.type` 可选 `sixel` / `kitty` / `iterm`（Windows Terminal 支持情况要自己试一次）。
* **手搓/编辑**：[durdraw/durdraw](https://github.com/durdraw/durdraw)（1.8k★ 终端 ASCII/ANSI 画板）。

### D. 已下好的样本 + 体检结论（`logos\`，16 个，50KB）

`fflogo` 列表里带行数的就是它们。按字形分两类：

* **纯 ASCII/box/block，零风险（13 个）**：`LierB-*`、`dlcgold-*`、`sama-*`（26 行 × 55 列，配色已烤进文件）
* **braille 画的，跟你现在这只猫同一路线，靠 Segoe UI Symbol 回退（3 个）**：`uwu-doraemon`、`uwu-sailorcat`、`uwu-anime-eyes`

排版建议：当前是「左图右文」，logo 宽 ≥ 28 或高 > 30 会把框挤出去 ——
用 `fflogo <名> -Big` 预览 **上下排版**（`--logo-position top`），`sama-*` 那种 40 行的人物图更适合它。

## fflogo：翻图 / 试图 / 定图

```powershell
fflogo                    # 列出可用图案（带行数，* = 当前）
fflogo LierB-rose         # 临时预览，不动配置
fflogo sama-anny -Big     # 用上下排版预览大图
fflogo sama-anny -Save    # 满意了写进 config.jsonc
fflogo -Reset             # 还原成默认（作者的猫）
```

## 常用改法

* **配色**：Catppuccin Mocha。`logo.color` = 猫的颜色（沿用上游映射）；`display.color.keys` = 标签色；
  每个 module 的 `keyColor` = 分节色（Hardware 蓝 / System 绿 / Now 黄）。
* **试 logo**：`ff --file ~\.configastfetchscii_flag.txt`、`ff -l windows`。
* **进度条**：`display.bar`（宽 8，`█`+`░`，粉色填充）；阈值在各 module 的 `percent` 里。
* **对齐**：这个 build 会忽略 `display.key.width`，键名是**手工补空格到 10 字符**的，
  新增模块时照抄这个宽度，否则值会错位。全部 16 行的值列实测都在第 49 视觉列。
* **盘符**：disk 模块故意**不写 `key`**。fastfetch 会自动在 key 后面追加挂点
  （`Disk (C:\)` / `Disk (D:\)` / `Disk (E:\)`）；一旦自己写了 `key`，这个后缀就没了。
  10 字符的标签宽度就是为它留的（`Disk (C:\)` 正好 10）。`{folder}` 这种占位符不存在，别试。
* **分隔线**：`custom` 模块想只输出线，`key` 必须写一个空格 `" "`；写 `""` 会退回默认键名 `Custom`。
* **噪声**：`gpu.hideType = "unknown"` 已经滤掉 MuMu / ZakoTech 两个虚拟显示适配器。
* **上游那个 Linux 味的 OS Age**（`stat -c %W /`）在 Windows 上必然失败，我没有搬过来。

## 自检

```powershell
fastfetch --version
ff                       # 完整渲染
ff --logo none           # 只看模块，用来区分是 logo 还是文字问题
ffedit ; ffedit logo     # 打开预设 / logo
```

## sama-* 那批人物的来历（fetch-sama 格式 ≠ fastfetch 格式）

`c-error/fetch-sama` 的 `configs/*.txt` 长这样：

```
color-scheme
[1]=208;168;136
...
ascii-art
[!]$1#***#**=***...
```

直接 `--file` 塞给 fastfetch 不会报错（exit 0），但 `color-scheme`、`[1]=…`、`[!]` 会被当图案打印出来 ——
**静默出错，只有肉眼看才发现**。`import_fetchsama.py` 负责转换：读 `[N]=r;g;b`，把 `$N` 换成真正的
`ESC[38;2;r;g;bm` 烤进文件（这样每张图带自己的配色，不用动 `config.jsonc` 的 `logo.color`），
并去掉 `[!]` 标记。原始文件留在 `logos/raw/`，再下新的（aquwa / evil）就：

```powershell
python ~\.configastfetch\import_fetchsama.py C:\pathquwa.txt
```

## ⚠️ neofetch 语法 ≠ fastfetch 语法（当前生效的 sailor-moon-cat 就是转换后用的）

`uwu-neofetch-art`、`ascii-art-neofetch` 这类仓库给的是 **neofetch** 格式：

```
(set_colors 7 11)              <- neofetch 指令行，fastfetch 会当图案原样打印
⠀${c1}⣿⣿${c2}⢀⣬${c1}⣿⣿       <- 颜色写 ${cN}；fastfetch 只认 $1..$9
```

塞给 `--file` 不会报错（exit 0），但屏幕上会多出一行 `(set_colors 7 11)`、
图案里夹着 `${c1}` 字样 —— **只有肉眼看才发现的静默错误**。

`import_neofetch.py` 做三件事：

1. 删掉 `(set_colors …)` / `(…)` 指令行（原值转成注释提示）；
2. `${cN}` → `$N`，颜色交回 `config.jsonc` 的 `logo.color` 管（改色不用重转）；
3. 裁掉四周空白（空格 + braille 空白 U+2800）—— sailor-moon-cat 从 67 列裁到 55 列，
   实测整屏最宽 116 列，**WT 默认 120 列窗口可以左右并排**。

```powershell
python ~\.config\fastfetch\import_neofetch.py C:\下载\xxx.txt        # 转换新图
python ~\.config\fastfetch\import_neofetch.py xxx.txt --no-crop     # 不裁边
# 原始文件都留在 logos\raw\，重转不会丢东西
```

## 当前生效的 logo

`logos/uwu-sailorcat.txt`（blyxyas 的彩色水手月亮猫，24 行）

* `logo.color.1 = #CDD6F4` ← 原 `c1`=white
* `logo.color.2 = #F9E2AF` ← 原 `c2`=bright_yellow（来自 `(set_colors 7 11)`）
* braille 字形：默认 profile（`profiles.defaults.font.face = Cascadia Mono`）原生支持；
  「PowerShell」profile（JetBrainsMono Nerd Font）走 Segoe UI Symbol 回退 —— 两边都实测能出图。

换回作者的猫：`fflogo -Reset`；再换回这只：`fflogo uwu-sailorcat -Save`。

## colorize.py：给图案做「分段渐变 + 按点数明暗」上色

上游 `sebicrb/Ascii-Art-` 的 `rei2.txt` 是**纯 braille、零颜色标记**（单色），而且四周大片留白、
底部还有 5 行想裁掉。`colorize.py` 就是干这个的：

1. `--cut N` 裁掉末尾 N 行；
2. 按行在 `PRESETS` 的锚点之间插值出**纵向渐变**（发色 → 肩颈 → 作战服）；
3. 同一行内再按 braille 字符的**点数**（`bin(cp-0x2800).count('1')`，0–8）连续调明暗：
   点少=高光、点多=阴影，图案自带的明暗关系就出来了（不是几条平色带）；
4. 颜色直接烤成 ANSI 写进文件，**不依赖** `config.jsonc` 的 `logo.color`；0 点字形（`⠀`）跳过换色省转义。

当前 `logos/rei2-color.txt` 用的锚点（对应行号按裁完的 26 行算）：

| 行 | 颜色 | 部位 |
|---|---|---|
| 0 | `#C3CBFE` | 头顶高光（淡紫白） |
| 2 | `#A9B8FD` | 标志性淡蓝发 |
| 6 | `#89B4FA` | 蓝 |
| 9 | `#6FA6EE` | 发尾压深 |
| 11 | `#B7C6F5` | 颈肩过渡 |
| 13 | `#DCE3F9` | 白色插入栓服（领口，亮） |
| 20 | `#CBD4F1` | 作战服中段 |
| 25 | `#B9C4E8` | 作战服下端（背光偏冷） |

```powershell
# 重新生成 / 微调（--dark 越小阴影越重，--light 越大高光越爆）
python ~\.config\fastfetch\colorize.py ~\.config\fastfetch\logos\rei2.txt `
       ~\.config\fastfetch\logos\rei2-color.txt --preset rei --dark 0.74 --light 1.28
```

文件对应关系：`logos/raw/rei2.txt` = 上游原件（53 行、未裁边、带空白）→
`logos/rei2.txt` = 裁边+裁尾 5 行的素白版 → `logos/rei2-color.txt` = 在其上上色（当前生效）。

## 脸部/脖子肤色区（rei2 用）

`colorize.py` 里 `REGIONS['rei']` 用**上游原图里唯一的字形串当锚点**定位皮肤格子（重新裁图也不会跑偏），
命中的行/段是：

| 行 | 锚点 | 尾随格 | 位置 |
|---|---|---|---|
| 6 | `⢿⣯⢤⣾⣤⡿` | 0 | 发际下的脸部第一排 |
| 7 | `⢠⢛⡞⣿⣿⣃` | 3（含 `⣱⣻⢟`） | 脸中 |
| 8 | `⢎⡿⣿⣿⣿⣫⣟` | 1（含 `⢁`） | 下巴 |
| 9 | `⠈⢣⢛⣖⣯⣾⣫⣿⣗` | 0 | 下颌/颈 |
| 10 | `⠉⢑⢽⡋⠿⠐⠛⠃` | 0 | 脖子 |

参数：`SKIN = '#F6DCCC'`（偏白肉色）、`SKIN_DK/SKIN_LT = 0.86/1.10`（皮肤专用窄明暗档，
比衣服的 0.74/1.28 窄，否则压暗会发褐发灰）、`SKIN_JAW = 0.93`（带右下点 dot8/128 的格子压 7% 当下颌颈影）。
实测 40 格，色阶 13 档，`#FFEBDA`（高光）→ `#C5B0A3`（阴影），全部落在暖色族，和蓝发形成对比。

两种读法都留着：

```powershell
$d = "$HOME\.config\fastfetch"
python $d\colorize.py $d\logos\rei2.txt $d\logos\rei2-color.txt --preset rei --dark .74 --light 1.28
python $d\colorize.py $d\logos\rei2.txt $d\logos\rei2-color-strict.txt --preset rei --exclude-dot8  # 带 dot8 的格子不填肤色
```

⚠️ 踩过的坑：**别给皮肤加"边缘向渐变掺色"**。皮肤区只有 6～9 格宽，每格都算边界，
掺 22% 的蓝色渐变直接把肉色洗成灰紫（`#A09BA2`）。默认 `edge_blend=0.0`，要软化边界最多 0.1 以内。

## 备份与当前状态

* **当前生效**：`logos/rei2.txt` —— 单色版（裁掉末尾 5 行 + 裁掉四周空白，26 行 × 27 列，总宽 96 列）
* **上色版备份**：`logos/backup/rei2-color.keep.txt`（另有一份带时间戳的），还原：
  ```powershell
  $d = "$HOME\.config\fastfetch"
  cp $d\logos\backup\rei2-color.keep.txt $d\logos\rei2-color.txt
  fflogo rei2-color -Save
  ```
  里面 `backup\README.txt` 记了参数快照（`SKIN/SKIN_JAW/SKIN_DK/LT`、锚点、40 格）与重生成命令。
* 也留了个「**只裁末尾 5 行、保留原图左边距**」的版本 `logos/rei2-fulltrim.txt`（48 行，宽 60 →
  并排需 129 列，默认 120 列窗口会自动走上下排版）。`fflogo` 列表里 `rei2` 是裁边版、`rei2-fulltrim` 是留边版。
* `fflogo` 只列 `logos\` 一层，`logos\backup\`、`logos\raw\` 不会进列表。

## RAM / Disk 占用条：分段阈值上色（不是单一色块）

```jsonc
"display": {
  "bar":     { "width": 12, "char": { "elapsed": "█", "total": "░" }, "border": null,
               "color": { "elapsed": "auto", "total": "#585B70" } },
  "percent": { "color": { "green": "#A6E3A1", "yellow": "#F9E2AF", "red": "#F38BA8" } }
},
"modules": [
  { "type": "memory", "percent": { "green": 60, "yellow": 85, "type": ["bar", "num", "num-color"] } },
  { "type": "disk",   "percent": { "green": 70, "yellow": 90, "type": ["bar", "num", "num-color"] } }
]
```

效果（本机实测，颜色是**固定色区**，填充踩到哪一段就变哪一段，数字也跟着变）：

| 指标 | 用量 | 条子 | 数字 |
|---|---|---|---|
| RAM | 76% | 绿×7 黄×2 灰×3 | 黄 |
| Disk (C:\) | 69% | 绿×8 灰×4 | 绿 |
| Disk (D:\) | 84% | 绿×8 黄×2 灰×2 | 黄 |
| Disk (E:\) | 81% | 绿×8 黄×2 灰×2 | 黄 |

踩坑记录（这版 fastfetch 2.71 的实测行为）：

* `display.bar` 是**全局**的，`memory`/`disk` 模块**没有** bar 覆盖项 —— 想按指标区分只能靠各自的
  `percent.green/yellow` 阈值（色区分界）与 `percent.type`。
* `bar.color.elapsed` 必须是 `"auto"`，才会走分段色；写固定 hex 就退化成单一色块（这就是之前那版的效果）。
* **`elapsed` 写渐变串 `"#A6E3A1-#F38BA8"` 不支持**：会原样吐出 `ESC[38;2;…-38;2;…m` 这种非法 SGR，
  终端里表现为不着色/乱码。别用。
* `percent.type`：`3`（=bar+num）只让条子分段着色，**数字仍是正文白**；要数字也按阈值变色必须加
  `num-color`（数组写法 `["bar","num","num-color"]`，或等价的数值 `11`）。
* `bar.border` 用 `leftElapsed`/`rightElapsed` 做胶囊时，实测只画得出左半边，所以这里保持 `null`。

想调风格：`width` 调分辨率（12 格时每 8.3% 一格）；阈值 `green/yellow` 决定色区从哪里开始变色；
三段颜色在 `display.percent.color` 统一改。

## RAM / Disk 用量条 v2：usagebar.ps1 逐格真彩渐变（当前生效）

上一节的「阈值分段」只有 3 色区（原生 bar 全局共享 + 阈值只有 green/yellow/red 三槽）。
现在换成 `command` 模块自绘：**16 格每格独立插值色，24-bit SGR 直接烤进输出**。

* **RAM**：蓝 → 薰衣草 → 紫 → 粉（`#89B4FA → #B4BEFE → #CBA6F7 → #F5C2E7`）
* **Disk**：青 → 绿（`#94E2D5 → #A6E3A1`）
* 轨道（未用部分）：同位置渐变色 ×0.28 暗度，且越过阈值的轨道微微泛红——危险区在哪一格一眼可见
* 越过阈值：填充尾部向黄(45%)/红(55%)过渡；**头格跳纯状态色**当进度"光标"
* 百分比数字：安全=家族色（RAM 蓝 / Disk 青），≥阈值黄，≥危险红
* 阈值：RAM 60/85，Disk 70/90；数据源纯 .NET（`ComputerInfo` + `DriveInfo`，不走 WMI）

```powershell
# 全部旋钮在 usagebar.ps1 顶部：BAR_W(格数)、$RAMP_RAM/$RAMP_DSK(渐变锚点)、
# $RAM_WARN/$RAM_DANG、$DSK_WARN/$DSK_DANG、$CACHE_TTL。改完重开终端或 fflogo 无关，直接 ff
notepad ~\.config\fastfetch\usagebar.ps1
```

### 性能与缓存

| 路径 | 耗时 |
|---|---|
| 脚本冷算（20s 内首次） | ~520 ms |
| 脚本命中缓存 | ~400 ms |
| 整窗启动（profile+fetch+缓存命中） | ~0.8 s（之前单色版 ~0.46 s） |

结果缓存在 `~\.config\fastfetch\.usage-cache`（TTL 20 秒）。连开终端窗基本都命中；
数字最多滞后 20 秒 —— 删掉缓存文件即强制刷新。

### 两个踩坑记录

1. fastfetch **直接 spawn `pwsh` 会报** `Child process exited with an error`（不管 -File 还是
   -Command、pwsh 还是 pwsh.exe）。解法：套一层 `cmd /c pwsh ...`（command 模块默认 shell 就是 cmd，
   text 里写全命令即可）。
2. 子脚本**必须**先 `[Console]::OutputEncoding = UTF8`，否则 `█`/`░` 出来是乱码
   （pwsh 7 重定向 stdout 的编码不保证 UTF-8，跟控制台代码页走）。

## 性能修正 v3：渐变计算挪进 shell 进程，fastfetch 只读缓存文件

v2 的 700ms 不是色块贵（转义序列就是文本，零成本），是 **command 模块每次渲染都孵一个全新
pwsh**（启动 215ms + Add-Type VB 122ms + 解析 ~100ms）。v3 拆成两半：

```
开窗时（Documents\PowerShell\Fastfetch.ps1 点源 usagebar.ps1）：
    shell 进程内调 Update-UsageBarCache   ~5ms（TTL 30s 内）/ ~150ms（过期才重算）
    └── 写 usagebar.cache.txt + .ts
fastfetch 渲染时：
    command 模块 = cmd /c type usagebar.cache.txt   ~30ms 全部渲染
```

| 指标 | v2（pwsh 子进程） | v3（进程内 + type） |
|---|---|---|
| fastfetch 渲染 | 434 ms | **30 ms** |
| `ff` 手动 | ~700 ms | **72 ms** |
| 开新窗 | 892 ms | **451 ms**（缓存被删冷算也只 473 ms） |

注意：缓存读取端没有 TTL——直接跑裸 `fastfetch`（不经过 profile/ff）会看到上次缓存；
正常路径（开窗 / `ff`）每次都先进程内刷新。强制刷新 = 删 `usagebar.cache.ts`。
