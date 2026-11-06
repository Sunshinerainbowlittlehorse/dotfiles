#!/bin/sh
# usagebar: RAM/Disk 16 格逐格真彩渐变条（Linux 版：POSIX sh + awk）
# fastfetch config.jsonc 调用: sh "$HOME/.config/fastfetch/usagebar.sh"
# 旋钮：BAR_W / RAM / DSK 渐变锚点 / WT_*、DT_* 阈值（awk BEGIN 段顶部）
exec awk '
function fg(c,    a) { split(c, a, /[ ,]+/); return sprintf("%s[38;2;%d;%d;%dm", ESC, a[1], a[2], a[3]) }
function blend(a, b, t,    x, y, o) {
  split(a, x, " "); split(b, y, " ")
  o = int(x[1]+(y[1]-x[1])*t) " " int(x[2]+(y[2]-x[2])*t) " " int(x[3]+(y[3]-x[3])*t)
  return o
}
function dim(c, k,    x) { split(c, x, " "); return int(x[1]*k) " " int(x[2]*k) " " int(x[3]*k) }
function bright(c, k,    x) { split(c, x, " "); return int(x[1]*k>255?255:x[1]*k) " " int(x[2]*k>255?255:x[2]*k) " " int(x[3]*k>255?255:x[3]*k) }
function ramp(n, stops, t,    i, f, x, a, b, o, k) {
  if (t <= 0) return stops[1]
  if (t >= 1) return stops[n]
  x = t * n; i = int(x); if (i >= n) i = n - 1; f = x - i
  split(stops[i+1], a, ","); split(stops[i+2], b, ",")
  o = ""
  for (k = 1; k <= 3; k++) o = o (k > 1 ? " " : "") int(a[k] + (b[k] - a[k]) * f)
  return o
}
function statec(p, w, d, safe) { return (p >= d) ? DANGER : (p >= w) ? WARN : safe }
function bar(p, stops, n, wt, dt, safe,    fill, res, i, base, cellpct, c, x) {
  fill = int(p / 100.0 * W + 0.5)
  if (fill == 0 && p > 0) fill = 1
  if (fill > W) fill = W
  res = ""
  for (i = 0; i < W; i++) {
    base = ramp(n, stops, i / (W - 1))
    cellpct = (i + 1) / W * 100
    if (i < fill) {
      c = base
      if (cellpct > dt)     c = blend(base, DANGER, 0.55)
      else if (cellpct > wt) c = blend(base, WARN, 0.45)
      if (i == fill - 1) {
        if (p >= dt)     c = DANGER
        else if (p >= wt) c = WARN
        else             c = bright(c, 1.15)
      }
      res = res fg(c) BLK
    } else {
      c = dim(base, 0.28)
      if (cellpct > dt)     c = blend(c, dim(DANGER, 0.85), 0.40)
      else if (cellpct > wt) c = blend(c, dim(WARN, 0.85), 0.30)
      res = res fg(c) TRK
    }
  }
  return res ESC "[0m"
}
function fmtsize(kb,    u, i, v) {
  split("B KB MB GB TB PB", u, " "); v = kb; i = 2
  while (v >= 1024 && i < 6) { v /= 1024; i++ }
  if (i <= 2) return sprintf("%d %s", int(v + 0.5), u[i])
  return sprintf("%.1f %s", v, u[i])
}
function row(icon, label, used, tot, p, stops, n, wt, dt, safe,    lab) {
  lab = substr(label "          ", 1, 10)
  return fg(KEYC) icon " " lab ESC "[0m " bar(p, stops, n, wt, dt, safe) fg(TXTC) " " fmtsize(used) " / " fmtsize(tot) " " fg(statec(p, wt, dt, safe)) "(" p "%)" ESC "[0m"
}
BEGIN {
  W = 16
  split("137,180,250 180,190,254 203,166,247 245,194,231", RAM, " ")   # 蓝->薰衣草->紫->粉
  split("148,226,213 166,227,161",                         DSK, " ")   # 青->绿
  WT_RAM = 60; DT_RAM = 85
  WT_DSK = 70; DT_DSK = 90
  KEYC = "137 180 250"; TXTC = "205 214 244"
  WARN = "249 226 175"; DANGER = "243 139 168"
  SAFE_RAM = "137 180 250"; SAFE_DSK = "148 226 213"
  ESC = "\033"
  ICON_RAM = "\356\277\205"    # U+EFC5
  ICON_DSK = "\357\202\240"    # U+F0A0
  BLK = "\342\226\210"; TRK = "\342\226\221"

  while ((getline line < "/proc/meminfo") > 0) {
    if (line ~ /^MemTotal:/)     { split(line, a, ":"); gsub(/[^0-9]/, "", a[2]); tot = a[2] + 0 }
    if (line ~ /^MemAvailable:/) { split(line, a, ":"); gsub(/[^0-9]/, "", a[2]); av  = a[2] + 0 }
  }
  close("/proc/meminfo")
  if (tot > 0) {
    used = tot - av
    print row(ICON_RAM, "RAM", used, tot, int(used / tot * 100 + 0.5), RAM, 4, WT_RAM, DT_RAM, SAFE_RAM)
  }
  while (("df -P -k" | getline line) > 0) {
    split(line, f, " ")
    if (f[1] !~ /^\//) continue
    if (f[1] ~ /^\/dev\/loop/) continue
    if (f[2] + 0 <= 0) continue
    mnt = f[6]
    lab = (mnt == "/") ? "Disk (/)" : "Disk (" mnt ")"
    if (length(lab) > 10) lab = substr(lab, 1, 10)
    print row(ICON_DSK, lab, f[3], f[2], int(f[3] / f[2] * 100 + 0.5), DSK, 2, WT_DSK, DT_DSK, SAFE_DSK)
  }
  close("df -P -k")
  exit
}
' "$@"
