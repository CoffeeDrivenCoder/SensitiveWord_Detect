#!/usr/bin/env python3
"""
从 konsheng/Sensitive-lexicon 的 Vocabulary 目录导入外部敏感词库。

用法:
  python3 scripts/import_konsheng_lexicon.py
"""

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENSITIVE_WORDS_DIR = os.path.join(REPO_ROOT, "data", "sensitive_words")
SOURCES_DIR = os.path.join(REPO_ROOT, "data", "sources")

OWNER = "konsheng"
REPO = "Sensitive-lexicon"
BRANCH = "main"
VOCABULARY_PATH = "Vocabulary"
SOURCE_NAME = "konsheng-Sensitive-lexicon"

API_URL = (
    f"https://api.github.com/repos/{OWNER}/{REPO}/contents/"
    f"{VOCABULARY_PATH}?ref={BRANCH}"
)
LICENSE_URL = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}/LICENSE"
SOURCE_REPO_URL = f"https://github.com/{OWNER}/{REPO}"
SOURCE_VOCABULARY_URL = f"{SOURCE_REPO_URL}/tree/{BRANCH}/{VOCABULARY_PATH}"


def fetch_bytes(url):
    parsed = urllib.parse.urlsplit(url)
    encoded_path = urllib.parse.quote(parsed.path)
    encoded_url = urllib.parse.urlunsplit((
        parsed.scheme,
        parsed.netloc,
        encoded_path,
        parsed.query,
        parsed.fragment,
    ))
    request = urllib.request.Request(
        encoded_url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "sensitive-stop-words-importer",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def fetch_json(url):
    return json.loads(fetch_bytes(url).decode("utf-8"))


def decode_text(data):
    for encoding in ("utf-8-sig", "utf-16", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def normalize_filename(filename):
    name = re.sub(r"[\\/]+", "_", filename).strip()
    return f"konsheng_{name}"


def split_words(content):
    comma_count = content.count(",")
    line_count = len(content.splitlines())
    if comma_count >= max(1, line_count // 2):
        raw_words = content.split(",")
    else:
        raw_words = content.splitlines()
    return [word.strip() for word in raw_words if word.strip()]


def normalize_words(content):
    seen = set()
    words = []
    for word in split_words(content):
        normalized = word.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        words.append(normalized)
    return words


def write_words(filename, words):
    os.makedirs(SENSITIVE_WORDS_DIR, exist_ok=True)
    output_path = os.path.join(SENSITIVE_WORDS_DIR, normalize_filename(filename))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(words))
        f.write("\n")
    return output_path


def write_source_files(imported_files):
    os.makedirs(SOURCES_DIR, exist_ok=True)

    readme_path = os.path.join(SOURCES_DIR, f"{SOURCE_NAME}.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"# {SOURCE_NAME}\n\n")
        f.write(f"- Repository: {SOURCE_REPO_URL}\n")
        f.write(f"- Vocabulary: {SOURCE_VOCABULARY_URL}\n")
        f.write("- License: MIT\n\n")
        f.write("Imported files:\n")
        for filename, count in imported_files:
            f.write(f"- {filename}: {count} words\n")

    try:
        license_text = decode_text(fetch_bytes(LICENSE_URL))
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"[WARN] 下载上游 LICENSE 失败: {exc}")
        return

    license_path = os.path.join(SOURCES_DIR, f"{SOURCE_NAME}.LICENSE")
    with open(license_path, "w", encoding="utf-8") as f:
        f.write(license_text.rstrip())
        f.write("\n")


def main():
    try:
        contents = fetch_json(API_URL)
    except (urllib.error.URLError, TimeoutError) as exc:
        raise SystemExit(f"下载 Vocabulary 文件列表失败: {exc}") from exc

    imported_files = []
    for item in contents:
        if item.get("type") != "file":
            continue
        filename = item.get("name", "")
        if not filename.endswith(".txt"):
            continue

        download_url = item.get("download_url")
        if not download_url:
            print(f"[SKIP] {filename}: 缺少 download_url")
            continue

        try:
            content = decode_text(fetch_bytes(download_url))
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"[WARN] 下载失败 {filename}: {exc}")
            continue

        words = normalize_words(content)
        if not words:
            print(f"[SKIP] {filename}: 没有有效词条")
            continue

        output_path = write_words(filename, words)
        imported_files.append((os.path.relpath(output_path, REPO_ROOT), len(words)))
        print(f"[OK] {filename} -> {os.path.relpath(output_path, REPO_ROOT)} ({len(words)} words)")

    if not imported_files:
        raise SystemExit("没有导入任何词库文件。")

    write_source_files(imported_files)
    print(f"\n导入完成: {len(imported_files)} 个文件。")


if __name__ == "__main__":
    main()
