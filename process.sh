#!/bin/bash
# Re-encode videos dropped into videos/input/ to the video frame's required
# format (see CLAUDE.md) and write them to videos/processed/.
#
#   ./process.sh          process everything pending in videos/input/
#   ./process.sh --watch  keep running, processing new files as they appear
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p videos/input videos/processed
shopt -s nullglob nocaseglob

encode() {
  local in="$1" out="$2"
  ffmpeg -y -nostdin -loglevel error -stats -i "$in" \
    -f lavfi -i anullsrc=r=48000:cl=stereo \
    -vf "scale=1728:1080,fps=30000/1001,format=yuv420p" \
    -c:v libx264 -profile:v high -level:v 4.0 -bf 0 -pix_fmt yuv420p \
    -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
    -c:a aac -b:a 128k -ar 48000 -ac 2 -shortest \
    -movflags +faststart -brand mp42 \
    "$out"
}

# A file dropped via Finder/copy may still be growing — wait until its size
# holds steady before touching it.
is_stable() {
  local a b
  a=$(stat -f%z "$1" 2>/dev/null) || return 1
  sleep 1
  b=$(stat -f%z "$1" 2>/dev/null) || return 1
  [[ "$a" == "$b" && "$a" != "0" ]]
}

run_once() {
  local f base out tmp
  for f in videos/input/*.{mp4,mov,m4v,avi,mkv,webm}; do
    base=$(basename "${f%.*}")
    out="videos/processed/$base.mp4"
    [[ -f "$out" && "$out" -nt "$f" ]] && continue
    is_stable "$f" || { echo "skipping $f (still copying)"; continue; }
    echo "processing: $f -> $out"
    tmp="videos/processed/.$base.tmp.mp4"
    if encode "$f" "$tmp"; then
      mv "$tmp" "$out"
      echo "done: $out"
    else
      rm -f "$tmp"
      echo "FAILED: $f" >&2
    fi
  done
}

if [[ "${1:-}" == "--watch" ]]; then
  echo "watching videos/input/ (ctrl-c to stop)"
  while true; do
    run_once
    sleep 2
  done
else
  run_once
fi
