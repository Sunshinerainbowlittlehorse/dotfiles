"""给 braille / ASCII 图案做「分段渐变 + 疏密二阶明暗」上色。

思路：
  1. 按行插值一个基准色（stops = [(行号, '#RRGGBB'), ...]，行号之外线性过渡）
  2. 同一行内再按字符疏密分三档：浓(阴影，压暗) / 中(基准) / 疏(高光，提亮)
  3. 只有颜色真的变了才写 ESC，避免文件膨胀
上色结果直接烤成 ANSI 写回文件，不依赖 config 的 logo.color。

用法：
    python colorize.py <输入> <输出> [--preset rei] [--cut 5] [--dark .80 --light 1.22]
                                                      [--exclude-dot8] [--no-skin]
  --exclude-dot8：皮肤区里带右下点(dot8/128)的格子不填肤色（按你原话的严格读法）
  默认：皮肤区整段填肤色，带 dot8 的压暗 12% 当下颌/颈部阴影
"""
import os, re, sys

# 明暗来源：braille 字符的点数（U+2800 起的 8 bit，popcount = 0..8 个点）
# 点数少 = 留白/高光，点数多 = 实心/阴影，所以做连续插值而不是两档。
DENSE = set('⣿⣾⣽⣻⢿⡿⣟⣯⣷⣶⣤⣴⣼⣸⣹⣺⣻⡽⡾⡿⣀⣁⣂⣄⣆⣇⣧⣩⣪⣫⣬⣭⣮⣰⣱⣲⣳⣴⣵⣶⣷⣸⣹⣺⣻⣼⣽⣾⣿#@%&')
LIGHT = set('⠀⠁⠂⠄⡀⢀⠐⠈⠉⠊⠋⠌⠍⠎⠏⡁⡂⡃⡄⡅⡆⡇⣀⣁⣂⣄⢁⢂⢄⢈⢐⢠⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟ .,\'`~"')

PRESETS = {
    # 绫波丽：淡蓝紫短发 -> 蓝色发 -> 发尾压深 -> 肩颈过渡 -> 白色插入栓服（下端微冷做体积感）
    'rei': [(0,  '#C3CBFE'),   # 头顶高光（淡紫白）
            (2,  '#A9B8FD'),   # 标志性淡蓝发
            (6,  '#89B4FA'),   # 蓝
            (9,  '#6FA6EE'),   # 发尾压深
            (11, '#B7C6F5'),   # 颈肩过渡（发梢投到肩上的阴影）
            (13, '#DCE3F9'),   # 白色作战服（领口，亮）
            (20, '#CBD4F1'),   # 作战服中段
            (25, '#B9C4E8'),   # 作战服下端（背光，冷一点）
            (30, '#A9B6E0')],
    # 备用：单色冷白（想对比用）
    'plain': [(0, '#CDD6F4'), (30, '#CDD6F4')],
}

# 皮肤区：用「上游原图里唯一的那串字形」当锚点定位（重新裁图也不会错位）
#   anchor = 定位串；tail = 再向右多吃几格（把 ⣱⣻⢟ / ⢁ 这些含进来）
#   color  = 该区的基准肤色；仍会按点数做明暗
SKIN = '#F6DCCC'          # 绫波丽的偏白肉色
SKIN_JAW = 0.93           # 带右下点(dot8)的格子稍微压暗当下颌/颈影；配 --exclude-dot8 则完全不填
SKIN_DK, SKIN_LT = 0.86, 1.10   # 皮肤专用的明暗档（比衣服的窄，不然会发褐发灰）
REGIONS = {
    'rei': [
        {'anchor': '⢿⣯⢤⣾⣤⡿',      'tail': 0, 'color': SKIN},   # 行6  脸（发际下第一排）
        {'anchor': '⢠⢛⡞⣿⣿⣃',      'tail': 3, 'color': SKIN},   # 行7  脸中 +⣱⣻⢟
        {'anchor': '⢎⡿⣿⣿⣿⣫⣟',     'tail': 1, 'color': SKIN},   # 行8  下巴 +⢁
        {'anchor': '⠈⢣⢛⣖⣯⣾⣫⣿⣗',  'tail': 0, 'color': SKIN},   # 行9  下颌/颈
        {'anchor': '⠉⢑⢽⡋⠿⠐⠛⠃',   'tail': 0, 'color': SKIN},   # 行10 脖子
    ],
}


def find_regions(lines, spec, exclude_dot8=False):
    """返回 {(row, col): color}；exclude_dot8=True 时跳过带右下点(bit128)的格子"""
    cells = {}
    for item in spec:
        a, tail, col = item['anchor'], item.get('tail', 0), item['color']
        for i, l in enumerate(lines):
            j = l.find(a)
            if j < 0:
                continue
            for k in range(j, min(len(l), j + len(a) + tail)):
                ch = l[k]
                o = ord(ch) - 0x2800
                if not (0 <= ord(ch) - 0x2800 <= 0xFF):
                    continue
                if exclude_dot8 and (o & 128):
                    continue
                cells[(i, k)] = col
    return cells


def hexs(rgb): return '#%02X%02X%02X' % tuple(max(0, min(255, round(v))) for v in rgb)
def to24(h):   return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


def ramp(stops, row):
    if row <= stops[0][0]:  return stops[0][1]
    if row >= stops[-1][0]: return stops[-1][1]
    for (r0, c0), (r1, c1) in zip(stops, stops[1:]):
        if r0 <= row <= r1:
            f = (row - r0) / max(1, (r1 - r0))
            a, b = to24(c0), to24(c1)
            return hexs(tuple(a[k] + (b[k] - a[k]) * f for k in range(3)))
    return stops[-1][1]


def shade(h, k):
    a = to24(h)
    return hexs(tuple(v * k for v in a))


def dots(ch):
    """0..8：这个字形画了几个点/多重，用于决定明暗档"""
    o = ord(ch)
    if 0x2800 <= o <= 0x28FF:
        return bin(o - 0x2800).count('1')
    if ch in ASCII_DENSITY:
        return ASCII_DENSITY[ch]
    return 5  # 其它可见字符当中间调


def tone(rgb, d, dk, lt):
    """点数 -> 亮度倍率：0 点最亮(lt)，8 点最暗(dk)，中间线性过渡。返回 (r,g,b) 元组"""
    k = lt + (dk - lt) * (d / 8.0)
    return tuple(max(0, min(255, round(v * k))) for v in rgb)


def colorize(text, stops, cut=0, dk=0.80, lt=1.22, regions=None, exclude_dot8=False, edge_blend=0.0):
    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    while lines and not lines[-1].strip():
        lines.pop()
    if cut:
        lines = lines[:-cut]
    reg = find_regions(lines, regions, exclude_dot8) if regions else {}

    def base_at(i, j, d):
        """该格基准色 + 明暗档：皮肤区用自己的色和窄明暗档，其它走行渐变"""
        c = reg.get((i, j))
        if c is None:
            return to24(ramp(stops, i)), dk, lt
        if exclude_dot8:
            return to24(c), SKIN_DK, SKIN_LT
        o = ord(lines[i][j]) - 0x2800
        if (o & 128) and SKIN_JAW:
            c = hexs(tuple(v * SKIN_JAW for v in to24(c)))
        if edge_blend:                      # 可选：只在真贴边时掺一点点（默认关，掺多了肉色会发灰）
            nb = [(i, j - 1), (i, j + 1), (i - 1, j), (i + 1, j)]
            if any(n not in reg for n in nb):
                a, b = to24(c), to24(ramp(stops, i))
                c = hexs(tuple(a[k] * (1 - edge_blend) + b[k] * edge_blend for k in range(3)))
        return to24(c), SKIN_DK, SKIN_LT

    out = []
    for i, l in enumerate(lines):
        cols = {}
        s, cur, buf = l.rstrip(), None, []
        for j, ch in enumerate(s):
            d = dots(ch)
            if d == 0:                      # 0 点 = 什么都不画，不必换色，省转义序列
                buf.append(ch); continue
            brgb, bdk, blt = base_at(i, j, d)
            c = cols.setdefault((brgb, d, bdk, blt), hexs(tone(brgb, d, bdk, blt)))
            if c != cur:
                if buf:
                    buf.append('\x1b[0m')
                r, g, b = to24(c)
                buf.append('\x1b[38;2;%d;%d;%dm' % (r, g, b))
                cur = c
            buf.append(ch)
        buf.append('\x1b[0m')
        out.append(''.join(buf))
    return '\n'.join(out) + '\n'


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__); return
    src, dst = a[0], a[1]
    preset = 'rei'
    if '--preset' in a: preset = a[a.index('--preset') + 1]
    cut = int(a[a.index('--cut') + 1]) if '--cut' in a else 0
    dk = float(a[a.index('--dark') + 1]) if '--dark' in a else 0.80
    lt = float(a[a.index('--light') + 1]) if '--light' in a else 1.22
    ex8 = '--exclude-dot8' in a
    regs = None if '--no-skin' in a else REGIONS.get(preset)
    txt = open(src, encoding='utf-8').read()
    body = colorize(txt, PRESETS[preset], cut, dk, lt, regs, ex8)
    if regs:
        pre = [l.rstrip() for l in txt.splitlines()]
        while pre and not pre[-1].strip():
            pre.pop()
        if cut:
            pre = pre[:-cut]
        n = len(find_regions(pre, regs, ex8))
        print('   皮肤区命中 %d 格（%s）' % (n, '严格：跳过 dot8' if ex8 else '默认：dot8 压暗当下颌影'))
    with open(dst, 'w', encoding='utf-8', newline='\n') as f:
        f.write(body)
    plain = re.sub(r'\x1b\[[0-9;]*m', '', body)
    nrow = len([l for l in plain.split('\n') if l.strip()])
    used = sorted(set(re.findall(r'\x1b\[38;2;(\d+;\d+;\d+)m', body)))
    print('%s -> %s : %d 行 x %d 列（裁掉末尾 %d 行），上色 %d 种，ESC %d 个'
          % (os.path.basename(src), os.path.basename(dst), nrow,
             max(len(l) for l in plain.split('\n')), cut, len(used), body.count('\x1b')))


if __name__ == '__main__':
    main()
