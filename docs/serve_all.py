"""serve.bat all 모드: ko/en 동시 빌드 + 자동 리로드 + HTTP 서빙."""

import functools
import http.server
import os
import subprocess
import sys
import threading
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.normpath(os.path.join(DOCS_DIR, "..", "output", "docs"))
HOST, PORT = "localhost", 8001
DEBOUNCE_SEC = 0.8

CONFIGS = [
    ("ko", os.path.join(DOCS_DIR, "mkdocs-ko.yml")),
    ("en", os.path.join(DOCS_DIR, "mkdocs-en.yml")),
]

WATCH_DIRS = [
    os.path.join(DOCS_DIR, "ko"),
    os.path.join(DOCS_DIR, "en"),
    os.path.join(DOCS_DIR, "hooks"),
    os.path.join(DOCS_DIR, "overrides"),
]


def log(msg):
    print(msg, flush=True)


def build(lang=None):
    targets = [c for c in CONFIGS if lang is None or c[0] == lang]
    for name, cfg in targets:
        t0 = time.time()
        r = subprocess.run(
            [sys.executable, "-m", "mkdocs", "build", "-f", cfg, "-q"],
            cwd=DOCS_DIR,
            capture_output=True,
            text=True,
        )
        elapsed = time.time() - t0
        if r.returncode == 0:
            log(f"  [{name}] built ({elapsed:.1f}s)")
        else:
            log(f"  [{name}] build FAILED:\n{r.stderr}")


class RebuildHandler(FileSystemEventHandler):
    def __init__(self):
        self._timer = None
        self._lock = threading.Lock()

    def _schedule(self):
        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(DEBOUNCE_SEC, self._rebuild)
            self._timer.start()

    def _rebuild(self):
        log("\nChange detected, rebuilding...")
        build()
        log("Ready. Reload your browser.\n")

    def on_modified(self, event):
        if not event.is_directory:
            self._schedule()

    def on_created(self, event):
        if not event.is_directory:
            self._schedule()

    def on_deleted(self, event):
        if not event.is_directory:
            self._schedule()


def serve():
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=OUTPUT_DIR
    )
    httpd = http.server.HTTPServer((HOST, PORT), handler)
    httpd.serve_forever()


def main():
    log("Building all languages...")
    build()

    log(f"\nServing at http://{HOST}:{PORT}")
    log(f"  Korean:  http://{HOST}:{PORT}/ko/")
    log(f"  English: http://{HOST}:{PORT}/en/")
    log("\nWatching for changes (auto-rebuild)...\n")

    server_thread = threading.Thread(target=serve, daemon=True)
    server_thread.start()

    observer = Observer()
    rebuild_handler = RebuildHandler()
    for d in WATCH_DIRS:
        if os.path.isdir(d):
            observer.schedule(rebuild_handler, d, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("\nShutting down...")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
