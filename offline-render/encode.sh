#!/bin/sh
set -eu
base=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
out="$base/yingxian-pagoda/public/offline"
mkdir -p "$out"
frames=${1:-"$base/offline-render/frames"}
size=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$frames/0001.png")
# 每帧都可直接定位，减少反向滚动时的解码等待；不插帧伪造细节。
ffmpeg -y -framerate 24 -i "$frames/%04d.png" -loop 1 -framerate 24 -i "$base/yingxian-pagoda/public/environment/chamber-haze.png" -filter_complex "[1:v]scale=$size,eq=saturation=0.3:brightness=-0.14:gamma=0.8[bg];[bg][0:v]overlay=shortest=1:format=auto,format=yuv420p[v]" -map '[v]' -r 24 -an -c:v libx264 -preset medium -crf 17 -g 1 -keyint_min 1 -movflags +faststart "$out/dougong.mp4"
ffmpeg -y -i "$out/dougong.mp4" -frames:v 1 -q:v 2 "$out/poster.jpg"
