"""把 neofetch 风格的 ascii 图案转成 fastfetch 直接可用的文件。

处理三类差异：
  1. `${c1}` / `${c2}` …   -> fastfetch 的 `$1` `$2` …（由 config 里 logo.color 上色）
     也兼容 `${c1}` 带属性的写法如 `${c1}text${c0}`（`${c0}` = 复位 -> 用 `$0`? 不认，直接丢掉）
  2. `(set_colors 7 11)` 之类的指令行 -> 删掉，并把 7/11 这两个 neofetch 调色板序号
     翻译成注释保留（真正的颜色由 logo.color 决定）
  3. 四周的空白（半角空格 + braille 空白 U+2800）-> 裁掉，省列数
     加 --no-crop 可保留原样

用法：
    python import_neofetch.py 输入文件[ ...] [--no-crop] [-o 输出目录]
输出：<原名>.txt（放 ~/.config/fastfetch/logos/，fflogo 会自动列出来）
"""
import os, re, sys

NEO_COLORS = {  # neofetch 调色板序号 -> 建议的 hex（仅作注释提示，实际颜色看 logo.color）
    '0': 'reset', '1': 'black', '2': 'red', '3': 'green', '4': 'yellow',
    '5': 'blue', '6': 'magenta', '7': 'white', '8': 'bright_black', '9': 'bright_red',
    '10': 'bright_green', '11': 'bright_yellow', '12': 'bright_blue', '13': 'bright_magenta',
    '14': 'bright_white', '90': 'dark_gray',
}
BLANKS = ' \t\u2800'


def convert(text, crop=True):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    hint = ''
    m = re.search(r'^\s*\(set_colors\s+(\S+)\s+(\S+)\s*\)\s*$', text, re.M)
    if m:
        hint = '原 (set_colors %s %s) -> c1=%s, c2=%s' % (
            m.group(1), m.group(2), NEO_COLORS.get(m.group(1), '?'), NEO_COLORS.get(m.group(2), '?'))
        text = re.sub(r'^\s*\(set_colors[^)]*\)\s*$', '', text, flags=re.M)
    # 其它 (xxx) 指令行
    text = re.sub(r'^\s*\([a-z_]+[^)]*\)\s*$', '', text, flags=re.M)
    # ${cN} -> $N ；${c0}/${cN} 复位之类 -> 丢弃
    text = re.sub(r'\$\{c([1-9])\}', r'$\1', text)
    text = re.sub(r'\$\{c0\}', '', text)
    text = re.sub(r'\$\{[^}]*\}', '', text)          # 剩下 neofetch 变量（$distro 之类）
    lines = text.split('\n')

    if crop:
        rows = [l for l in lines if l.strip(BLANKS)]
        left = min(len(l) - len(l.lstrip(BLANKS)) for l in rows)
        right = max(len(l.rstrip(BLANKS)) for l in rows)
        lines = [l.rstrip(BLANKS)[left:right] for l in lines]
        while lines and not lines[0].strip(BLANKS):
            lines.pop(0)
        while lines and not lines[-1].strip(BLANKS):
            lines.pop()
    body = '\n'.join(l.rstrip() for l in lines)
    return body + '\n', hint


def main():
    args = sys.argv[1:]
    crop = '--no-crop' not in args
    args = [a for a in args if a != '--no-crop']
    outdir = os.path.expanduser(r'~\.config\fastfetch\logos')
    if '-o' in args:
        i = args.index('-o'); outdir = args[i+1]; del args[i:i+2]
    if not args:
        print(__doc__); return
    os.makedirs(outdir, exist_ok=True)
    for src in args:
        raw = open(src, encoding='utf-8', errors='replace').read()
        out, hint = convert(raw, crop)
        base = os.path.basename(src).split('.txt')[0].split('.ascii')[0]
        dst = os.path.join(outdir, base + '.txt')
        with open(dst, 'w', encoding='utf-8', newline='\n') as f:
            f.write(out)
        rows = [l for l in out.split('\n') if l.strip()]
        toks = sorted(set(re.findall(r'\$(\d)', out)))
        print('%-24s -> %-22s %2dx%-3d 色标=%s %s' % (os.path.basename(src), os.path.basename(dst),
              len(rows), max((len(l) for l in rows), default=0), '$' + ', $'.join(toks) if toks else '无',
              ('| ' + hint) if hint else ''))


if __name__ == '__main__':
    main()
