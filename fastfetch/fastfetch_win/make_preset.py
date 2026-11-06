"""生成/更新 fastfetch 预设：
  - ~/.config/fastfetch/config.jsonc   预设本体
  - ~/.config/fastfetch/ascii_flag.txt 备选块元素旗（不碰作者的猫 ascii.txt！）
改宽度/标签对齐请改下面的常量，然后 `python ~/.config/fastfetch/make_preset.py`
"""
import os

cfgdir = os.path.expanduser(r'~\.config\fastfetch')
os.makedirs(cfgdir, exist_ok=True)

# ---------- 备选 logo：Windows 11 四色块旗（写到 ascii_flag.txt）----------
W, H, GX = 15, 11, 2
TOP = "\u2597" + "\u2584" * (W - 2) + "\u2596"
MID = "\u2588" * W
BOT = "\u259d" + "\u2580" * (W - 2) + "\u2598"
rows = []
for band in range(2):
    for r in range(H):
        ch = TOP if r == 0 else (BOT if r == H - 1 else MID)
        c1, c2 = band * 2 + 1, band * 2 + 2
        rows.append("$%d%s" % (c1, ch) + " " * GX + "$%d%s" % (c2, ch))
    if band == 0:
        rows.append("")
with open(os.path.join(cfgdir, 'ascii_flag.txt'), 'w', encoding='utf-8', newline='\n') as f:
    f.write("\n".join(rows) + "\n")

# ---------- 布局常量 ----------
LW = 10          # key 标签宽度（手工补空格；这个 build 忽略 display.key.width）
                 # 取 10 是为了容纳 disk 自动带的 "Disk (C:\)"
INNER = 63       # 框内宽度
DASH = "\u2500"


def rule_top(title):
    fill = INNER - len(title) - 2
    a = fill // 2
    return "\u250c" + DASH * a + " " + title + " " + DASH * (fill - a) + "\u2510"


def rule_bot():
    return "\u2514" + DASH * INNER + "\u2518"


def lab(s):
    assert len(s) <= LW, 'label too long: %r' % s
    return s + " " * (LW - len(s))


BOX = {
    'HW_T': rule_top('Hardware'), 'HW_B': rule_bot(),
    'SY_T': rule_top('System'),   'SY_B': rule_bot(),
    'NW_T': rule_top('Now'),      'NW_B': rule_bot(),
}
for v in BOX.values():
    assert len(v) == INNER + 2, (v, len(v))

TEMPLATE = r"""// ╔══════════════════════════════════════════════════════════════════╗
//  fastfetch 美化预设 · Catppuccin Mocha · Windows 11
//  路径: %USERPROFILE%/.config/fastfetch/config.jsonc
//  logo: 用 `fflogo` 切换（列表 / 预览 / -Save 固定 / -Reset 回默认猫）
//
//  · braille 类图案（猫 / rei / uwu）依赖字体里的 U+2800 字形：默认 profile 的
//    Cascadia Mono 原生有；「PowerShell」profile 的 JetBrainsMono Nerd Font 没有，
//    靠 Windows Terminal 回退到本机 Segoe UI Symbol（braille 256/256）补齐。
//    万一显示成方框/空心：把 settings.json 里 "face" 写成
//    "JetBrainsMono Nerd Font, Cascadia Mono"（主字体不变，只补字形），
//    或换不依赖回退的 logo： fflogo ascii_flag / ff --file ~/.config/fastfetch/ascii_flag.txt
//  · 手动预览： PowerShell 里直接敲  ff
//  · 本次启动不自动跑： $env:FASTFETCH_AUTO='0' 后再开新窗口
//
//  动手改之前两句：① 标签是手工补空格到 10 字符的，加模块记得补满；
//  ② disk 故意不写 key —— 一写 key 就把 fastfetch 自动加的盘符 (C:\) 顶掉了。
// ╚══════════════════════════════════════════════════════════════════╝
{
  "$schema": "https://github.com/fastfetch-cli/fastfetch/raw/dev/doc/json_schema.json",

  "logo": {
    // logo 文件用 `fflogo <名字> -Save` 切换；重新生成这份配置时会自动保留你当前选的那个
    "type": "file",
    "source": "__LOGO_SOURCE__",
    // 上游作者的原色映射（$1..$9 由 logo.color 自动替换）
    "color": {
      "1": "#CDD6F4",
      "2": "#F9E2AF",   // neofetch 转来的图常用 $2 做高亮（原 c2=bright_yellow）
      "3": "#F5C2E7",
      "4": "#F5E0DC",
      "5": "#F9E2AF",
      "6": "#A6E3A1",
      "7": "#94E2D5",
      "8": "#89DCEB",
      "9": "#74C7EC"
    },
    "padding": { "top": 1, "left": 1, "right": 3 },
    // auto：终端放不下时自动改成上下排版，宽图不会把右边的框挤没
    "position": "auto",
    "printRemaining": true
  },

  "display": {
    "separator": " ",
    "color": {
      "keys": "#CBA6F7",
      "title": "#F5C2E7",
      "output": "#CDD6F4",
      "separator": "#585B70"
    },
    "key": { "type": "both-1" },
    "size": { "binaryPrefix": "jedec", "ndigits": 1 },
    "freq": { "ndigits": 2 },
    "duration": { "abbreviation": true },
    "percent": {
      "ndigits": 0,
      // 三段交通灯色：安全 / 注意 / 危险（multicolor bar 的色区就按这个分）
      "color": { "green": "#A6E3A1", "yellow": "#F9E2AF", "red": "#F38BA8" }
    },
    "bar": {
      "width": 12,
      "char": { "elapsed": "\u2588", "total": "\u2591" },
      "border": null,
      // elapsed 必须写 "auto"：交给 percent 阈值做分段着色。
      // 写固定色 = 单一色块；写 "#xxx-#yyy" 渐变串这版不支持（会吐出非法 SGR）
      "color": { "elapsed": "auto", "total": "#585B70" }
    },
    "disableLinewrap": true
  },

  "modules": [
    { "type": "title", "format": "{user-name-colored}{at-symbol-colored}{host-name-colored}" },
    "break",

    { "type": "custom", "key": " ", "format": "__HW_T__", "outputColor": "__BLUE__" },
    { "type": "host",   "key": "__L_MACHINE__", "keyColor": "__BLUE__", "format": "{name} ({version})" },
    { "type": "cpu",    "key": "__L_CPU__", "keyColor": "__BLUE__", "format": "{name} @ {freq-max}" },
    { "type": "gpu",    "key": "__L_GPU__", "keyColor": "__BLUE__", "hideType": "unknown", "format": "{name} [{type}]" },
    // RAM/Disk 用量条由 usagebar.ps1 自绘：16 格逐格真彩渐变（RAM 蓝紫系 / Disk 青绿系），
    // 尾部越过阈值向黄/红过渡 + 头格跳状态色 + 百分比数字同步变色。
    // 渐变计算发生在 shell 进程内（Fastfetch.ps1 点源刷新缓存），这里只 type 缓存文件，
    // 不再每次渲染孵 pwsh（那 ~230ms 就是之前 700ms 的主要来源）。
    // 旋钮：usagebar.ps1 的 BAR_W / 渐变锚点 / 阈值 / CACHE_TTL。
    { "type": "command", "key": " ",
      "text": "type __USAGECACHE__ 2>nul",
      "splitLines": true, "useOutput": "stdout" },
    { "type": "custom", "key": " ", "format": "__HW_B__", "outputColor": "__BLUE__" },

    "break",

    { "type": "custom", "key": " ", "format": "__SY_T__", "outputColor": "__GREEN__" },
    { "type": "os",       "key": "__L_OS__", "keyColor": "__GREEN__" },
    { "type": "kernel",   "key": "__L_KERNEL__", "keyColor": "__GREEN__", "format": "{release}" },
    { "type": "shell",    "key": "__L_SHELL__", "keyColor": "__GREEN__" },
    { "type": "terminal", "key": "__L_TERM__", "keyColor": "__GREEN__", "format": "{pretty-name}{?version} ({version}){?}" },
    { "type": "display",  "key": "__L_SCREEN__", "keyColor": "__GREEN__", "format": "{width}x{height} @ {refresh-rate}Hz" },
    { "type": "wmtheme",  "key": "__L_THEME__", "keyColor": "__GREEN__" },
    { "type": "custom", "key": " ", "format": "__SY_B__", "outputColor": "__GREEN__" },

    "break",

    { "type": "custom", "key": " ", "format": "__NW_T__", "outputColor": "__YELLOW__" },
    { "type": "uptime",   "key": "__L_UPTIME__", "keyColor": "__YELLOW__", "format": "{hours}h {minutes}m" },
    { "type": "battery",  "key": "__L_BATTERY__", "keyColor": "__YELLOW__" },
    { "type": "datetime", "key": "__L_CLOCK__", "keyColor": "__YELLOW__", "format": "{year}-{month-pretty}-{day-pretty} {hour-pretty}:{minute-pretty}" },
    { "type": "custom", "key": " ", "format": "__NW_B__", "outputColor": "__YELLOW__" },

    { "type": "colors", "key": " ", "symbol": "circle", "paddingLeft": 3 }
  ]
}
"""

PAL = {
    '__BLUE__': "#89B4FA", '__GREEN__': "#A6E3A1", '__YELLOW__': "#F9E2AF",
}
sub = dict(PAL)
sub.update({
    '__HW_T__': BOX['HW_T'], '__HW_B__': BOX['HW_B'],
    '__SY_T__': BOX['SY_T'], '__SY_B__': BOX['SY_B'],
    '__NW_T__': BOX['NW_T'], '__NW_B__': BOX['NW_B'],
    '__L_MACHINE__': lab('Machine'), '__L_CPU__': lab('CPU'), '__L_GPU__': lab('GPU'),
    '__L_RAM__': lab('RAM'),
    '__L_OS__': lab('OS'), '__L_KERNEL__': lab('Kernel'), '__L_SHELL__': lab('Shell'),
    '__L_TERM__': lab('Term'), '__L_SCREEN__': lab('Screen'), '__L_THEME__': lab('Theme'),
    '__L_UPTIME__': lab('Uptime'), '__L_BATTERY__': lab('Battery'), '__L_CLOCK__': lab('Clock'),
    '__USAGECACHE__': os.path.expanduser('~/.config/fastfetch/usagebar.cache.txt').replace('/', chr(92)).replace(chr(92), chr(92)*2),
})
# 保留用户当前的 logo 选择（否则重建配置会退回默认那只猫）
cur_cfg = os.path.join(cfgdir, 'config.jsonc')
cur_src = '%USERPROFILE%/.config/fastfetch/ascii.txt'
if os.path.exists(cur_cfg):
    import re as _re
    _txt = open(cur_cfg, encoding='utf-8').read()
    _m = _re.search(r'"source"[^"]*"([^"]*)"', _txt)
    if _m and _m.group(1):
        cur_src = _m.group(1)

out = TEMPLATE
sub['__LOGO_SOURCE__'] = cur_src
for k, v in sub.items():
    out = out.replace(k, v)
assert '__' not in out, [ln for ln in out.splitlines() if '__' in ln]

with open(os.path.join(cfgdir, 'config.jsonc'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(out)
print("config.jsonc ok (label=%d inner=%d); ascii_flag.txt %d rows; ascii.txt untouched" % (LW, INNER, len(rows)))
