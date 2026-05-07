#!/usr/bin/env python3
"""本地敏感词检测测试前端服务。"""

import argparse
import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

from check_text import SENSITIVE_WORDS_DIR, check_text, load_sensitive_words

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(REPO_ROOT, "web")


class SensitiveCheckHandler(BaseHTTPRequestHandler):
    entries = []
    max_reasons = 20

    def log_message(self, format, *args):
        return

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/check":
            self.send_json(404, {"error": "Not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_json(400, {"error": "Invalid content length"})
            return

        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError:
            self.send_json(400, {"error": "Invalid JSON"})
            return

        text = payload.get("text", "")
        max_reasons = payload.get("maxReasons", self.max_reasons)
        if not isinstance(text, str):
            self.send_json(400, {"error": "text must be a string"})
            return

        try:
            max_reasons = max(1, min(100, int(max_reasons)))
        except (TypeError, ValueError):
            max_reasons = self.max_reasons

        result = check_text(text, self.entries, max_reasons)
        result["length"] = len(text)
        self.send_json(200, result)

    def send_static(self, head_only=False):
        path = unquote(self.path.split("?", 1)[0])
        if path == "/":
            path = "/index.html"

        relative_path = path.lstrip("/")
        file_path = os.path.abspath(os.path.join(WEB_DIR, relative_path))
        if not file_path.startswith(os.path.abspath(WEB_DIR) + os.sep):
            self.send_error(403)
            return

        if not os.path.isfile(file_path):
            self.send_error(404)
            return

        content_type, _ = mimetypes.guess_type(file_path)
        with open(file_path, "rb") as f:
            body = f.read()

        self.send_response(200)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def do_GET(self):
        self.send_static()

    def do_HEAD(self):
        self.send_static(head_only=True)


def main():
    parser = argparse.ArgumentParser(description="启动敏感词检测测试前端。")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--max-reasons", type=int, default=20)
    args = parser.parse_args()

    SensitiveCheckHandler.entries = load_sensitive_words(SENSITIVE_WORDS_DIR)
    SensitiveCheckHandler.max_reasons = max(1, args.max_reasons)

    server = ThreadingHTTPServer((args.host, args.port), SensitiveCheckHandler)
    print(f"检测前端已启动: http://{args.host}:{args.port}")
    print(f"已加载词条: {len(SensitiveCheckHandler.entries)}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")


if __name__ == "__main__":
    main()
