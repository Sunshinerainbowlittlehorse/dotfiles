"""把 fetch-sama 的 configs/*.txt 转成 fastfetch 能直接吃的 logo 文件。

fetch-sama 的格式是：
    color-scheme
    [1]=r;g;b ... [9]=r;g;b
    accent-color / highlight-color      <- 忽略
    ascii-art
    [!]$1####$2+..                      <- 图案行，[!] 是行标记，$N 引用上面的色号

fastfetch 的 logo.type=file 只认 $1..$9 + config 里的 logo.color（一套颜色管所有图）。
所以这里把每个图**自带的配色直接烤成 ANSI 转义**写进文件，换图不用改 config 颜色。
图案只用 ASCII 字符（# % @ * + = - : .），任何等宽字体都不会翻车。

用法：
    python import_fetchsama.py <输入文件...> [-o 输出目录]
"""
import os, re, sys

HEADERS = ('color-scheme', 'accent-color', 'highlight-color', 'ascii-art')


def convert(path):
    txt = open(path, encoding='utf-8', errors='replace').read().replace('\r\n', '\n')
    mode, colors, art = None, {}, []
    for line in txt.split('\n'):
        s = line.strip()
        if s in HEADERS:
            mode = s
            continue
        if not s:
            continue
        if mode == 'color-scheme':
            m = re.match(r'^\[(\d)\]=(\d+;\d+;\d+)$', s)
            if m:
                colors[int(m.group(1))] = m.group(2)
        elif mode == 'ascii-art':
            if s.startswith('[!]'):
                s = s[3:]
            art.append(s)
    if not art:
        raise SystemExit('没找到 ascii-art 段：%s' % path)

    def sub(m):
        rgb = colors.get(int(m.group(1)))
        return ('\x1b[38;2;%sm' % rgb) if rgb else m.group(0)

    out = [re.sub(r'\$(\d)', sub, l) + '\x1b[0m' for l in art]
    return '\n'.join(out) + '\n', colors


def main():
    args = [a for a in sys.argv[1:]]
    outdir = os.path.expanduser(r'~\.config\fastfetch\logos')
    if '-o' in args:
        i = args.index('-o')
        outdir = args[i + 1]
        del args[i:i + 2]
    if not args:
        print(__doc__)
        return
    os.makedirs(outdir, exist_ok=True)
    for src in args:
        body, colors = convert(src)
        dst = os.path.join(outdir, os.path.basename(src).split('.txt')[0] + '.txt')
        with open(dst, 'w', encoding='utf-8', newline='\n') as f:
            f.write(body)
        plain = re.sub(r'\x1b\[[0-9;]*m', '', body)
        rows = [l for l in plain.split('\n') if l.strip()]
        print('%-22s -> %-46s %dx%d 列, 自带 %d 色'
              % (os.path.basename(src), dst, len(rows), max(len(l) for l in rows), len(colors)))


if __name__ == '__main__':
    main()
