# Inner Sphere Video Generator

`index.html` is a fixed 1728x1080 stage whose element positions are
pre-mirrored for the frame's horizontally-mirrored display (circle left,
rects right). Never scale or reposition it responsively — captures must be
pixel-exact.

## Video processing

Drop source videos into `videos/input/` and run `./process.sh` (or
`./process.sh --watch` to keep it running). Each file is re-encoded to the
required format below and written to `videos/processed/<name>.mp4`. The
`videos/` directory is gitignored. Already-processed files are skipped
unless the input is newer than the output.

# Video frame SD card

This SD card feeds an external video frame that only plays videos encoded a
specific way. Before putting any video on this card, re-encode it with the
recipe below. Videos that don't match (too high resolution/level, variable
frame rate, no audio track) fail to play or display incorrectly.

## Required format

- Container: MP4 (`mp42` brand), `-movflags +faststart`
- Video: H.264 High profile, level 4.0, yuv420p, bt709, no B-frames (`-bf 0`)
- Resolution: 1728x1080 (the frame's screen is 16:10 — 16:9 content gets
  stretched and looks squished horizontally)
- Frame rate: constant 29.97 fps (`fps=30000/1001`)
- Audio: required even for silent videos — stereo AAC, 48 kHz (use
  `anullsrc` for a silent track)

## Encoding command

```sh
ffmpeg -y -i INPUT.mp4 -f lavfi -i anullsrc=r=48000:cl=stereo \
  -vf "scale=1728:1080,fps=30000/1001,format=yuv420p" \
  -c:v libx264 -profile:v high -level:v 4.0 -bf 0 -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
  -c:a aac -b:a 128k -ar 48000 -ac 2 -shortest \
  -movflags +faststart -brand mp42 \
  OUTPUT.mp4
```

Verify with:

```sh
ffprobe -v error -show_entries stream=codec_name,profile,level,width,height,avg_frame_rate -of default=noprint_wrappers=1 OUTPUT.mp4
```

Eject the card safely before unplugging — it's FAT-formatted and files can
corrupt otherwise.
