#!/usr/bin/env python3
"""Convert YouTube rolling auto-caption VTT into clean timed cues.

YouTube's auto-captions repeat the previous line at the top of each cue and
insert 10ms filler cues between them. We keep only the newly-spoken line from
each real cue, strip the inline <00:00:00.000><c> word timings, and close each
cue at the start of the next one.

  ./vtt-to-json.py videos/source/orient.en.vtt captions.json
"""
import json
import re
import sys

TAG = re.compile(r"<[^>]*>")
TIMING = re.compile(
    r"^(\d+:\d+:\d+\.\d+)\s+-->\s+(\d+:\d+:\d+\.\d+)"
)


def secs(ts):
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def parse(path):
    blocks = open(path, encoding="utf-8").read().split("\n\n")
    cues = []
    for block in blocks:
        lines = block.strip().split("\n")
        head = next((l for l in lines if TIMING.match(l)), None)
        if not head:
            continue
        m = TIMING.match(head)
        start, end = secs(m.group(1)), secs(m.group(2))
        if end - start < 0.05:            # rollover filler cue
            continue
        body = lines[lines.index(head) + 1:]
        text = ""
        for line in body:                  # last non-empty line is the new text
            stripped = TAG.sub("", line).strip()
            if stripped:
                text = stripped
        if text:
            cues.append({"t": round(start, 3), "e": round(end, 3), "s": text})

    # Drop consecutive duplicates, then close each cue at the next one's start
    out = []
    for c in cues:
        if out and out[-1]["s"] == c["s"]:
            out[-1]["e"] = c["e"]
            continue
        out.append(c)
    for i in range(len(out) - 1):
        out[i]["e"] = min(out[i]["e"], out[i + 1]["t"])
    return out


src = sys.argv[1] if len(sys.argv) > 1 else "videos/source/orient.en.vtt"
dst = sys.argv[2] if len(sys.argv) > 2 else "captions.json"
cues = parse(src)
json.dump(cues, open(dst, "w", encoding="utf-8"), ensure_ascii=False)
print(f"{len(cues)} cues -> {dst}")
