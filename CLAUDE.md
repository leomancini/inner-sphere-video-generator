# Inner Sphere Video Generator

`index.html` is a fixed 1728x1080 stage whose element positions are
pre-mirrored for the frame's horizontally-mirrored display (circle left,
caption panel right). Never scale or reposition it responsively — captures
must be pixel-exact.

Two areas:

- `#circle` (875x875 at 96,100) plays the source video. `#video --zoom`
  pushes in from the top edge (`cover` already fills the height of a square,
  so `object-position` has no vertical effect — the scale is what crops).
  1 = full height, 2 = top half.
- `#captions` (435x822 at 1238,128) is the old `#rect-top` and `#rect-bottom`
  merged into one panel spanning both plus the 252px gap between them. It
  shows caption text only — no timestamps — scrolling to hold the active line
  at `ANCHOR` with past lines dimmed.

The frame is mounted upside down, so both areas are turned 180 deg — `#rotor`
for the footage, `#caption-inner` for the text. A half-turn keeps each box's
dimensions, so neither area needs the width/height swap a quarter-turn would
force on the caption panel. The cue list still scrolls "up" and the soft mask
at the ends of `#cue-view` still fades top-to-bottom in their own coordinate
space; both read correctly once the frame inverts them, so don't "fix" the
direction.

Content is otherwise unmirrored — only the element positions are pre-mirrored.
If the display's horizontal mirroring turns out to also apply, the caption
text will read backwards and will need `scaleX(-1)` on top of the rotation.

## Captions

`vtt-to-json.py` converts a YouTube auto-caption `.vtt` into `captions.json`
(`[{t, e, s}]`, seconds). YouTube's rolling format repeats the previous line
at the top of every cue and inserts 10ms filler cues between them; the script
keeps only the newly-spoken line, strips the inline word-timing tags, and
closes each cue at the next one's start.

    ./vtt-to-json.py videos/source/orient.en.vtt captions.json

Fetch the source with yt-dlp (`--write-auto-subs --sub-langs "en.*"
--sub-format vtt`). Keep yt-dlp current — a stale build fails extraction
outright with "Requested format is not available".

## Previewing

Run `./serve.py` (port 8080) rather than `python -m http.server`: the latter
ignores Range headers, so a long video plays from the start but can never
seek, which breaks scrubbing.

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
