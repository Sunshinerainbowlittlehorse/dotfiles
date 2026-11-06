#!/bin/sh
# fastfetch_linux 安装器：复制到 ~/.config/fastfetch 并替换 __HOME__ 占位符
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
DST="${FASTFETCH_DST:-$HOME/.config/fastfetch}"
mkdir -p "$DST"
for f in ascii.txt ascii_flag.txt usagebar.sh; do cp "$SRC/$f" "$DST/"; done
[ -d "$SRC/logos" ] && cp -r "$SRC/logos" "$DST/"
sed "s|__HOME__|$HOME|g" "$SRC/config.jsonc" > "$DST/config.jsonc"
chmod +x "$DST/usagebar.sh" 2>/dev/null || true
echo "installed -> $DST"
echo "config 里的 logo/usagebar 路径已指向 $HOME"
echo "试跑: sh $DST/usagebar.sh   然后: fastfetch"
