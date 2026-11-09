#!/usr/bin/env python
"""Serve the SHAIDA frontend and proxy /v1 to the backend, on one origin.

Why this exists: the frontend calls its API with relative URLs, so serving both the
static build and the API from a single origin needs no CORS configuration and makes
the whole app reachable behind one public URL. It is a static file server plus a
transparent reverse proxy, nothing more.

Usage::

    python scripts/serve_public.py [--port 12000] [--api http://127.0.0.1:8000]

The frontend must be built first:  cd frontend && npm run build
"""

from __future__ import annotations

import argparse
import http.client
import http.server
import os
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "frontend", "dist")

# Hop-by-hop headers must not be forwarded by a proxy (RFC 7230 §6.1).
HOP_BY_HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}


def parse_target(url: str) -> tuple[str, int]:
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "http" or not parts.hostname:
        raise SystemExit(f"--api must be an http:// URL, got {url!r}")
    return parts.hostname, parts.port or 80


class Handler(http.server.SimpleHTTPRequestHandler):
    api_host = "127.0.0.1"
    api_port = 8000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST, **kwargs)

    def log_message(self, fmt: str, *args) -> None:  # quieter, but still honest
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _proxy(self) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None

        headers = {k: v for k, v in self.headers.items() if k.lower() not in HOP_BY_HOP}
        headers["Host"] = f"{self.api_host}:{self.api_port}"

        conn = http.client.HTTPConnection(self.api_host, self.api_port, timeout=30)
        try:
            conn.request(self.command, self.path, body=body, headers=headers)
            resp = conn.getresponse()
            payload = resp.read()
        except OSError as exc:
            self.send_error(502, f"backend unreachable: {exc}")
            return
        finally:
            conn.close()

        self.send_response(resp.status)
        for key, value in resp.getheaders():
            if key.lower() not in HOP_BY_HOP:
                self.send_header(key, value)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/v1/"):
            self._proxy()
        else:
            super().do_GET()

    def do_HEAD(self) -> None:  # noqa: N802
        if self.path.startswith("/v1/"):
            self._proxy()
        else:
            super().do_HEAD()

    def do_POST(self) -> None:  # noqa: N802
        if self.path.startswith("/v1/"):
            self._proxy()
        else:
            self.send_error(405, "only the API accepts POST")

    def do_OPTIONS(self) -> None:  # noqa: N802
        if self.path.startswith("/v1/"):
            self._proxy()
        else:
            self.send_error(405)

    def end_headers(self) -> None:
        # A stale cached index.html would pin users to an old asset hash.
        if self.path.endswith("/") or self.path.endswith(".html") or "text/html" in (
            self.headers.get("Accept") or ""
        ):
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def translate_path(self, path: str) -> str:
        # Single-page app: unknown non-API paths fall back to index.html.
        resolved = super().translate_path(path)
        if not os.path.exists(resolved) or os.path.isdir(resolved):
            index = os.path.join(DIST, "index.html")
            if os.path.exists(index):
                return index
        return resolved


def main() -> int:
    port = int(os.environ.get("PORT", "12000"))
    api = os.environ.get("SHAIDA_API", "http://127.0.0.1:8000")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=port)
    parser.add_argument("--api", default=api)
    args = parser.parse_args()

    if not os.path.isdir(DIST):
        raise SystemExit(f"frontend build not found at {DIST}; run: cd frontend && npm run build")

    Handler.api_host, Handler.api_port = parse_target(args.api)
    server = http.server.ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    print(f"serving {DIST} on http://0.0.0.0:{args.port}  (proxying /v1 -> {args.api})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
