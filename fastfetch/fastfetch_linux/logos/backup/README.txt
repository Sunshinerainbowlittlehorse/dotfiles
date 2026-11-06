rei2 上色版的备份与复原配方（备份时间 20261106-1535）

固定备份文件 : rei2-color.keep.txt    （fflogo 不列子目录，想切回直接 fflogo <路径> 或复制回 logos\）
复原命令     : cp ~\.config\fastfetch\logos\backup\rei2-color.keep.txt ~\.config\fastfetch\logos\rei2-color.txt
重新生成     : python ~\.config\fastfetch\colorize.py ~\.config\fastfetch\logos\rei2.txt                       ~\.config\fastfetch\logos\rei2-color.txt --preset rei --dark 0.74 --light 1.28
参数快照     : SKIN=#F6DCCC  SKIN_JAW=0.93  SKIN_DK/LT=0.86/1.10  edge_blend=0  皮肤区 40 格
严格版备份   : rei2-color-strict.20261106-1535.txt（--exclude-dot8，只填 10 格）
