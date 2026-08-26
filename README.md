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

The footage and captions are from **"Northwest Orient Airlines 1950s Asia
Travelogue: High Road to the Orient"**, posted by **PeriscopeFilm**:

<https://www.youtube.com/watch?v=XJdnAymPRzI>

PeriscopeFilm is an archival film channel; this is a 1950s airline promotional
travelogue. The video itself is not in this repo — `videos/` is gitignored.
`captions.json` is generated from the video's YouTube auto-captions by
`vtt-to-json.py`, so the transcript is machine-made and has the transcription
errors you would expect of it.

To fetch the source again:

    yt-dlp -f "bv*[height<=1080]+ba/b" --merge-output-format mp4 \
      --write-auto-subs --sub-langs "en.*" --sub-format vtt \
      -o "videos/source/orient.%(ext)s" \
      "https://www.youtube.com/watch?v=XJdnAymPRzI"
    ./vtt-to-json.py videos/source/orient.en.vtt captions.json

480p is the highest resolution YouTube holds for this upload.
