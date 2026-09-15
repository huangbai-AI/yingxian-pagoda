#!/bin/sh
set -eu
base=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
public="$base/yingxian-pagoda/public"
ffmpeg -y -framerate 24 -i "$base/offline-render/sharp/frames-dof/%04d.png" -loop 1 -framerate 24 -i "$public/environment/chamber-haze.png" -filter_complex '[1:v]scale=1920:1080,eq=saturation=0.3:brightness=-0.14:gamma=0.8[bg];[bg][0:v]overlay=shortest=1:format=auto,format=yuv420p[v]' -map '[v]' -r 24 -an -c:v libx264 -preset medium -crf 14 -g 1 -keyint_min 1 -movflags +faststart "$public/offline/dougong-hd.mp4"
ffmpeg -y -i "$public/offline/dougong-hd.mp4" -frames:v 1 -q:v 2 "$public/offline/poster-hd.jpg"
ffmpeg -y -i "$base/offline-render/sharp/frames-dof/0001.png" -i "$public/environment/chamber-haze.png" -filter_complex '[1:v]scale=1920:1080,eq=saturation=0.3:brightness=-0.14:gamma=0.8[bg];[bg][0:v]overlay=format=auto,format=yuvj420p[v]' -map '[v]' -frames:v 1 -q:v 2 "$public/offline/detail-hd.jpg"
