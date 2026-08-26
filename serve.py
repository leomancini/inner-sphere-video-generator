#!/usr/bin/env python3
"""Static server with HTTP Range support, for previewing the stage locally.

python -m http.server ignores Range headers, so a long video served from it
can play from the start but never seek. The frame capture needs to scrub, so
this handler answers Range requests with a proper 206.

  ./serve.py [port]        default 8080
"""
import http.server
import os
import re
import socketserver
import sys

RANGE = re.compile(r"bytes=(\d*)-(\d*)")


class Handler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        header = self.headers.get("Range")
        if not header:
            return super().send_head()

        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()
        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None

        size = os.fstat(f.fileno()).st_size
        m = RANGE.match(header)
        if not m:
            f.close()
            self.send_error(400, "Malformed Range")
            return None

        start, end = m.group(1), m.group(2)
        if start == "":                       # suffix range: last N bytes
            start = max(0, size - int(end))
            end = size - 1
        else:
            start = int(start)
            end = int(end) if end else size - 1
        end = min(end, size - 1)
        if start > end:
            f.close()
            self.send_error(416, "Requested Range Not Satisfiable")
            return None

        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        f.seek(start)
        return RangeFile(f, end - start + 1)

    def end_headers(self):
        if "Accept-Ranges" not in self._headers_buffer_keys():
            self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def _headers_buffer_keys(self):
        return b"".join(getattr(self, "_headers_buffer", []) or []).decode(
            "latin-1", "replace"
        )

    def log_message(self, fmt, *a):
        pass


class RangeFile:
    """Wraps a file so copyfile() stops after the requested slice."""

    def __init__(self, f, remaining):
        self.f = f
        self.remaining = remaining

    def read(self, n=-1):
        if self.remaining <= 0:
            return b""
        if n < 0 or n > self.remaining:
            n = self.remaining
        data = self.f.read(n)
        self.remaining -= len(data)
        return data

    def close(self):
        self.f.close()


class Server(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True

    def handle_error(self, request, client_address):
        # A <video> element cancels its range request on every seek, which
        # surfaces here as a broken pipe. That is normal, not a fault -- only
        # let genuine errors reach the log.
        if not isinstance(sys.exc_info()[1], (BrokenPipeError, ConnectionResetError)):
            super().handle_error(request, client_address)


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f"serving {os.getcwd()} on http://127.0.0.1:{port}")
Server(("127.0.0.1", port), Handler).serve_forever()
