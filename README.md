# Inner Sphere Video Generator

A fixed 1728x1080 stage that drives an external video frame. The circle plays
archival footage; the panel beside it shows one line of time-synced caption at
a time. Both areas are turned 270 degrees for the way the frame is mounted, and
the stage's element positions are pre-mirrored for its mirrored display.

See [CLAUDE.md](CLAUDE.md) for the layout details, the caption pipeline, and the
encoding recipe the frame's SD card requires.

## Running it

    ./serve.py            # http://127.0.0.1:8080 — serves with Range support
    ./process.sh          # re-encode videos/input/ for the frame's SD card

`./serve.py` rather than `python -m http.server`: the latter ignores Range
headers, so a long video plays from the start but can never seek.

## Source footage

The footage and captions are from **"Manila, Shanghai, Tokyo and Hong Kong in
the 60s"**, posted by **TRNGL**:

<https://www.youtube.com/watch?v=1smEmvVxSR0>

The video itself is not in this repo — `videos/` is gitignored. `captions.json`
is generated from the video's YouTube captions by `vtt-to-json.py`; this
upload's captions already carry punctuation and sentence case, so they need no
cleanup pass.

To fetch the source again:

    yt-dlp -f "137+ba/bv*[height<=1080][vcodec^=avc1]+ba/b[height<=1080]" \
      --merge-output-format mp4 \
      --write-auto-subs --sub-langs "en.*" --sub-format vtt \
      -o "videos/source/asia60s.%(ext)s" \
      "https://www.youtube.com/watch?v=1smEmvVxSR0"
    ./vtt-to-json.py videos/source/asia60s.en.vtt captions.json

The upload goes to 4K, but 1080p is fetched deliberately: the circle is 875px
and the footage is scaled ~1.14x at the default zoom, so more resolution would
not show. The picture inside that 1920x1080 frame is 4:3 — 1440x1080
pillarboxed at x=240 — which sets the zoom floor documented in `index.html`.
